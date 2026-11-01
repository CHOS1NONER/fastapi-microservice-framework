"""
迁移配置：按微服务隔离，每个服务独立的 migrations 目录与 DB 连接
"""
import importlib
from pathlib import Path

from common.db.database_manager import async_mysql_url

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SERVICES_DIR = PROJECT_ROOT / "services"


def list_services() -> list[str]:
    """返回所有微服务名称"""
    if not SERVICES_DIR.exists():
        return []
    return [d.name for d in SERVICES_DIR.iterdir() if d.is_dir() and not d.name.startswith("_")]


def get_service_root(service_name: str) -> Path:
    """服务根目录，如 services/iam"""
    path = SERVICES_DIR / service_name
    if not path.exists():
        raise ValueError(f"Service not found: {service_name}. Available: {list_services()}")
    return path


def get_migrations_dir(service_name: str) -> Path:
    """服务专属 migrations 目录"""
    return get_service_root(service_name) / "migrations"


def get_versions_dir(service_name: str) -> Path:
    """服务专属 versions 目录"""
    return get_migrations_dir(service_name) / "versions"


def get_db_url_for_service(service_name: str) -> str:
    """从服务的 settings 动态获取 DB_URL"""
    try:
        mod = importlib.import_module(f"services.{service_name}.main")
        settings = getattr(mod, "settings", None)
        if settings is None:
            raise ValueError(f"services.{service_name}.main has no 'settings' object")
        return async_mysql_url(settings.DB_URL)
    except ImportError as e:
        raise ValueError(f"Cannot load settings for service '{service_name}': {e}")
