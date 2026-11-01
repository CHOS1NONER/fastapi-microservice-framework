import os
import sys

sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.path.append(".")

from common.core.service_bootstrap import ServiceBootstrap
from services.product.config import settings
from services.product.order.view.order_view import router as order_router
from services.product.product.view.product_view import router as product_router

bootstrap = ServiceBootstrap(settings, service_file=__file__)
app = bootstrap.create_app()
app.include_router(product_router, prefix="/api", tags=["product"])
app.include_router(order_router, prefix="/api", tags=["order"])


if __name__ == "__main__":
    bootstrap.run()
