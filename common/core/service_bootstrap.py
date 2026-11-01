import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from starlette.exceptions import HTTPException

import clients
from common.auth import AuthMiddleware, allow_anonymous
from common.core.base_settings import BaseServiceSettings
from common.core.runtime import clear_runtime, init_runtime
from common.db.database_manager import DatabaseManager
from common.middleware import *
from common.utils.domain_error import DomainError
from common.utils.jwt_helper import JWTHelper
from common.utils.logger_helper import LoggerHelper
from common.utils.rpc_error import RpcError


class ServiceBootstrap:
    """
    服务启动引导基类。
    """

    def __init__(self, settings: BaseServiceSettings, *, service_file: str):
        """
        Args:
            settings:      服务配置实例
            service_file:  服务入口文件路径（传 __file__），用于推断 service_root
        """
        self.settings = settings
        self.service_root = os.path.dirname(os.path.abspath(service_file))
        self.logger: LoggerHelper = None
        self.db_manager: DatabaseManager = None

    # ───────── 子类扩展点 ─────────

    async def on_startup(self, app: FastAPI):
        """服务特有的启动逻辑（如额外客户端初始化等）"""

    async def on_shutdown(self, app: FastAPI):
        """服务特有的关闭逻辑"""

    def register_middlewares(self, app: FastAPI):
        """
        注册中间件。默认注册 CORS + Auth + DBSession，子类可覆盖以追加自定义中间件。
        注意：最后添加的中间件最先执行。
        """
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        app.add_middleware(TracingMiddleware)

        # 鉴权中间件（按 docs/auth.md）
        jwt_helper = JWTHelper(
            secret_key=getattr(self.settings, "JWT_SECRET_KEY", "change_me"),
            algorithm=getattr(self.settings, "JWT_ALGORITHM", "HS256"),
            logger_instance=self.logger,
        )
        app.state.jwt_helper = jwt_helper
        # 中间件只解析身份；是否必须登录由路由 Depends(require_auth) 决定
        app.add_middleware(AuthMiddleware, logger_instance=self.logger)
        app.add_middleware(DBSessionMiddleware)

    def register_exception_handlers(self, app: FastAPI):
        """注册异常处理器。子类可覆盖以追加自定义处理器。"""
        app.add_exception_handler(RpcError, rpc_exception_handler)
        app.add_exception_handler(DomainError, domain_exception_handler)
        app.add_exception_handler(RequestValidationError, validation_exception_handler)
        app.add_exception_handler(HTTPException, http_exception_handler)
        app.add_exception_handler(Exception, general_exception_handler)

    def create_app(self) -> FastAPI:
        """创建并配置 FastAPI 应用实例。"""
        self.logger = LoggerHelper.new_logger(
            self.settings.SERVICE_NAME,
            self.settings.LOG_PATH,
            LoggerHelper.DEBUG,
        )

        app = FastAPI(
            title=self.settings.SERVICE_NAME,
            docs_url=f"/{self.settings.SERVICE_NAME}/docs",
            redoc_url=f"/{self.settings.SERVICE_NAME}/redoc",
            openapi_url=f"/{self.settings.SERVICE_NAME}/openapi.json",
            lifespan=self._lifespan,
        )

        self.register_middlewares(app)
        self.register_exception_handlers(app)
        self._setup_openapi_auth(app)
        app.state.logger = self.logger

        @app.get("/health", dependencies=[Depends(allow_anonymous)])
        async def health_check():
            return {"status": "ok"}

        return app

    def _setup_openapi_auth(self, app: FastAPI):
        """
        注册 Bearer 安全方案；只有 Depends(require_auth) / HTTPBearer 的接口会显示小锁。
        登录等公开接口不要求全局 security。
        """

        def custom_openapi():
            if app.openapi_schema:
                return app.openapi_schema
            schema = get_openapi(
                title=app.title,
                version=getattr(self.settings, "VERSION", "1.0.0"),
                routes=app.routes,
            )
            schema.setdefault("components", {})["securitySchemes"] = {
                "HTTPBearer": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                }
            }
            app.openapi_schema = schema
            return schema

        app.openapi = custom_openapi

    def run(self, reload: bool = False):
        """通过 uvicorn 启动服务。"""
        print(
            f"服务启动: http://127.0.0.1:{self.settings.HTTP_PORT}"
            f"/{self.settings.SERVICE_NAME}/docs"
        )
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=self.settings.HTTP_PORT,
            workers=self.settings.WORKERS,
            reload=reload,
        )

    # ───────── 内部实现 ─────────

    @asynccontextmanager
    async def _lifespan(self, app: FastAPI):
        logger = self.logger
        try:
            # Outbox 模型挂到 Base.metadata，供迁移工具发现
            import common.db.outbox_model  # noqa: F401

            self.db_manager = DatabaseManager(
                db_url=self.settings.DB_URL,
                pool_size=self.settings.DB_POOL_SIZE,
                max_overflow=self.settings.DB_MAX_OVERFLOW,
                logger=logger,
            )
            await self.db_manager.connect_database()

            # 表结构改走 Alembic 迁移，避免与同事本地库/create_all 互相抢建表
            # 空库请先：uv run python scripts/migrator.py init -s <服务>
            #           uv run python scripts/migrator.py -s <服务> up
            # await self.db_manager.create_all(Base)

            app.state.db_manager = self.db_manager

            init_runtime(db_manager=self.db_manager, logger=logger)

            await self.on_startup(app)

            yield

        except Exception:
            logger.exception("lifespan startup failed")
            raise

        finally:
            try:
                await self.on_shutdown(app)
            except Exception as e:
                logger.error(f"on_shutdown error: {e}", exc_info=True)

            if self.db_manager:
                try:
                    await self.db_manager.close()
                except Exception as e:
                    logger.error(f"Failed to close database connection: {e}")

            await clients.aclose()

            clear_runtime()
            logger.info(f"[{self.settings.SERVICE_NAME}] shutting down...")
