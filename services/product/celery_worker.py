"""
商品服务 Celery worker（含 Outbox 定时投递，仓库根目录启动）：

    uv run celery -A services.product.celery_worker worker -B -Q product --concurrency=10 -l info

``-B`` 启用 Beat：每分钟扫本库 outbox_message，失败最多重投 3 次。
"""

from common.tasks import celery_app, setup_worker
from services.product.config import Settings

setup_worker(Settings(SERVICE_NAME="product_worker"), packages=["services.product.product"])

app = celery_app
