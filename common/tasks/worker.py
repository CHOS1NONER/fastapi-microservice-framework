from celery.signals import worker_process_init, worker_process_shutdown

from common.core.base_settings import BaseServiceSettings
from common.core.runtime import clear_runtime, get_db_manager, init_runtime
from common.db.database_manager import DatabaseManager
from common.tasks.celery_app import celery_app
from common.tasks.pool import AsyncIOPool
from common.utils.logger_helper import LoggerHelper


def _queue_name(settings: BaseServiceSettings) -> str:
    name = settings.SERVICE_NAME
    for suffix in ("_worker", "_service"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def setup_worker(settings: BaseServiceSettings, packages: list[str]) -> None:
    """
    worker 入口调用：使用 AsyncIOPool，进程启动时初始化 DB，退出时关闭。

    packages 下的 ``tasks.py`` 会被自动发现注册。
    同时注册 Outbox 定时投递（每 60s），需加 ``-B`` 启动 Beat。
    """
    # 确保 Outbox 表模型与投递任务被加载
    from common.db import outbox_model as _outbox_model
    from common.tasks import outbox_tasks as _outbox_tasks

    _ = (_outbox_model, _outbox_tasks)


    celery_app.conf.worker_pool = "common.tasks.pool:AsyncIOPool"
    queue = _queue_name(settings)
    celery_app.conf.beat_schedule = {
        "outbox-dispatch-every-minute": {
            "task": "outbox.dispatch",
            "schedule": 60.0,
            "options": {"queue": queue},
        }
    }

    async def startup():
        logger = LoggerHelper.new_logger(settings.SERVICE_NAME, settings.LOG_PATH, LoggerHelper.DEBUG)
        db_manager = DatabaseManager(
            db_url=settings.DB_URL,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            logger=logger,
        )
        await db_manager.connect_database()
        # 表结构改走 Alembic 迁移，勿在 Worker 启动时 create_all
        # await db_manager.create_all(Base)
        init_runtime(db_manager=db_manager, logger=logger)

    async def shutdown():
        await get_db_manager().close()
        clear_runtime()

    @worker_process_init.connect(weak=False)
    def init_db(**kwargs):
        AsyncIOPool.run_in_pool(startup)

    @worker_process_shutdown.connect(weak=False)
    def close_db(**kwargs):
        AsyncIOPool.run_in_pool(shutdown)

    celery_app.autodiscover_tasks(packages, force=True)

