from celery import Celery, Task
from starlette.concurrency import run_in_threadpool

from common.core.base_settings import BaseServiceSettings
from common.tasks.async_support import current_request, patch_autoretry

patch_autoretry()


class AppTask(Task):
    @property
    def request(self):
        req = current_request.get()
        if req is not None and getattr(req, "task", None) == self.name:
            return req
        return self._get_request()

    async def async_delay(self, *args, **kwargs):
        """异步调用任务"""
        return await run_in_threadpool(self.apply_async, args, kwargs)

    async def apply_async_await(
        self, args=None, kwargs=None, task_id=None, producer=None, link=None, link_error=None, shadow=None, **options
    ):
        return await run_in_threadpool(
            self.apply_async, args, kwargs, task_id, producer, link, link_error, shadow, **options
        )


def _route_by_service(name: str, args, kwargs, options, task=None, **kw) -> dict | None:
    """任务名前缀即队列：``inventory.record_flow`` → 队列 ``inventory``。"""
    service, sep, _ = name.partition(".")
    # outbox.dispatch 由 Beat 的 options.queue 指定到各服务队列，不按前缀路由
    if sep and service not in ("celery", "outbox"):
        return {"queue": service}
    return None



celery_app = Celery("app", broker=BaseServiceSettings().CELERY_BROKER_URL, task_cls=AppTask)

celery_app.conf.task_default_queue = "celery"
celery_app.conf.task_routes = (_route_by_service,)
celery_app.conf.task_serializer = "json"
celery_app.conf.accept_content = ["json"]
celery_app.conf.task_ignore_result = True
celery_app.conf.worker_prefetch_multiplier = 1  # 默认值是4，预取数量等于这个值乘以 worker_concurrency
celery_app.conf.broker_connection_retry_on_startup = True


async def async_send_task(name: str, *args, **kwargs):
    """按任务名投递，用于跨服务调用（不导入对方服务的任务代码）。"""
    return await run_in_threadpool(celery_app.send_task, name, args, kwargs)
