"""
模型加载器：按服务扫描 models，将指定服务的 Model 注册到 Base.metadata
"""
import importlib.util
import logging
from pathlib import Path

log = logging.getLogger(__name__)


def discover_models_for_service(service_root: str, project_root: str) -> None:
    """
    扫描 service_root 下的 models 目录，导入该服务的 Model。
    使用 project_root 计算完整模块名（如 services.iam.user.models.user），避免多服务同名包冲突。
    """
    root = Path(service_root)
    proot = Path(project_root)
    if not root.exists():
        return

    for models_dir in root.rglob("models"):
        if not models_dir.is_dir():
            continue
        try:
            models_dir.relative_to(root)
        except ValueError:
            continue
        for py_file in sorted(models_dir.glob("*.py")):
            if py_file.name == "__init__.py":
                continue
            _load_module(py_file, proot)


def _load_module(py_file: Path, project_root: Path) -> None:
    """动态导入模块，模块名为相对 project_root 的包路径（如 services.iam.user.models.user）。"""
    try:
        rel = py_file.relative_to(project_root)
        parts = rel.with_suffix("").parts
        module_name = ".".join(parts)

        spec = importlib.util.spec_from_file_location(module_name, py_file)
        if spec is None or spec.loader is None:
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception as e:
        log.warning("Failed to load model module %s: %s", py_file, e, exc_info=True)
