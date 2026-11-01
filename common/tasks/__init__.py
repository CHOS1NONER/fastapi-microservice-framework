"""
Celery 异步任务（AsyncIOPool + Outbox 定时投递）

- celery_app: 全局 Celery 应用，任务名前缀即队列名
- AsyncIOPool: worker 池，async 任务原生跑在事件循环上
- async_send_task: 按任务名跨服务投递（不落 Outbox，适合可丢场景）
- setup_worker: 各服务 worker 入口调用，初始化 DB、Outbox Beat、发现任务
"""

from common.tasks.celery_app import async_send_task, celery_app
from common.tasks.pool import AsyncIOPool
from common.tasks.worker import setup_worker

__all__ = ["AsyncIOPool", "async_send_task", "celery_app", "setup_worker"]
