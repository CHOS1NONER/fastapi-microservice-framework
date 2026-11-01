"""
库存服务 Celery worker（含 Outbox 定时投递，仓库根目录启动）：

    uv run celery -A services.inventory.celery_worker worker -B -Q inventory --concurrency=20 -l info

``-B`` 启用 Beat：每分钟扫本库 outbox_message，失败最多重投 3 次。
"""


from common.tasks import celery_app, setup_worker
from services.inventory.config import Settings

setup_worker(Settings(SERVICE_NAME="inventory_worker"), packages=["services.inventory.inventory"])

app = celery_app
