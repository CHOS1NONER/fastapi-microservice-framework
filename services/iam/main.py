import os
import sys

sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.path.append(".")

from common.core.service_bootstrap import ServiceBootstrap
from services.iam.auth.view.login_view import router as login_router
from services.iam.config import settings
from services.iam.user.view.user_view import router as user_router

bootstrap = ServiceBootstrap(settings, service_file=__file__)
app = bootstrap.create_app()
app.include_router(user_router, prefix="/api", tags=["user"])
app.include_router(login_router, prefix="/api", tags=["auth"])

if __name__ == "__main__":
    bootstrap.run()
