import os
import sys

sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.path.append(".")

from common.core.service_bootstrap import ServiceBootstrap
from services.inventory.config import settings
from services.inventory.inventory.view.inventory_view import router as inventory_router

bootstrap = ServiceBootstrap(settings, service_file=__file__)
app = bootstrap.create_app()
app.include_router(inventory_router, prefix="/api", tags=["inventory"])

if __name__ == "__main__":
    bootstrap.run()
