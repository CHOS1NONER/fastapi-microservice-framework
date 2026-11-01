"""
Alembic 迁移执行环境（按微服务隔离）
- 从 MIGRATE_SERVICE 读取服务名
- 仅加载该服务的 Model
- 使用该服务的 settings.DB_URL
"""
import os
import sys
from pathlib import Path

service_name = os.environ.get("MIGRATE_SERVICE")
if not service_name:
    raise RuntimeError("MIGRATE_SERVICE env var required. Use: migrate -s <service> <cmd>")

# env.py 位于 services/<svc>/migrations/env.py -> 4 层到项目根
_project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool

from common.base.base_table_model import Base
from common.db.migrator.config import get_db_url_for_service, get_service_root
from common.db.migrator.model_loader import discover_models_for_service

# 仅加载当前服务的 Model（传入 project_root 以使用完整模块名）
service_root = get_service_root(service_name)
discover_models_for_service(str(service_root), str(_project_root))
# Outbox 表在 common，需显式挂到 metadata，否则 generate 扫不到
import common.db.outbox_model  # noqa: E402, F401

target_metadata = Base.metadata

config = context.config
config.set_main_option("sqlalchemy.url", get_db_url_for_service(service_name))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def process_revision_directives(context, revision, directives):
    """
    阻止在没有任何结构变更时生成空迁移文件：
    - 如果 upgrade_ops 为空，则清空 directives，等价于“跳过生成”
    """
    if not directives:
        return

    script = directives[0]
    upgrade_ops = getattr(script, "upgrade_ops", None)
    if upgrade_ops is not None and upgrade_ops.is_empty():
        directives[:] = []
        print("[migrate] 未检测到任何结构变更，已跳过空迁移文件生成。")


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        process_revision_directives=process_revision_directives,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    import asyncio

    from sqlalchemy.ext.asyncio import create_async_engine

    url = get_db_url_for_service(service_name)

    def do_run(connection):
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
        )
        with context.begin_transaction():
            context.run_migrations()

    async def run():
        connectable = create_async_engine(url, poolclass=pool.NullPool)
        async with connectable.connect() as connection:
            await connection.run_sync(do_run)
        await connectable.dispose()

    asyncio.run(run())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
