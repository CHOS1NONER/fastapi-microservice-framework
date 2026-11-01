"""
迁移 CLI：按微服务独立迁移，手动触发，自动生成/执行/回滚

用法:
  python -m common.db.migrator list                      # 列出所有微服务
  python -m common.db.migrator init -s iam               # 初始化 iam 的 migrations 目录
  python -m common.db.migrator -s iam generate [msg]     # 为 iam 自动生成迁移
  python -m common.db.migrator -s iam up                 # 执行 iam 的迁移
  python -m common.db.migrator -s iam down [steps]       # 回滚 iam 的迁移
  python -m common.db.migrator -s iam history            # 查看 iam 迁移历史
  python -m common.db.migrator -s iam current            # 查看 iam 当前版本
"""
import argparse
import os
import shutil
import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


def _get_alembic_config(service_name: str):
    from alembic.config import Config

    from common.db.migrator.config import get_migrations_dir

    migrations_dir = get_migrations_dir(service_name)
    if not (migrations_dir / "env.py").exists():
        raise FileNotFoundError(
            f"Service '{service_name}' migrations not initialized. Run: migrate init -s {service_name}"
        )

    cfg = Config(_project_root / "alembic.ini")
    cfg.set_main_option("script_location", str(migrations_dir))
    return cfg


def _ensure_service(name: str):
    from common.db.migrator.config import get_service_root, list_services
    if name not in list_services():
        raise ValueError(f"Unknown service: {name}. Available: {list_services()}")
    return get_service_root(name)


def _run_with_service(service_name: str, fn):
    os.environ["MIGRATE_SERVICE"] = service_name
    try:
        return fn()
    finally:
        os.environ.pop("MIGRATE_SERVICE", None)


def cmd_init(service_name: str) -> int:
    """初始化服务的 migrations 目录"""
    from common.db.migrator.config import get_migrations_dir, get_versions_dir

    _ensure_service(service_name)
    migrations_dir = get_migrations_dir(service_name)
    versions_dir = get_versions_dir(service_name)
    template_dir = Path(__file__).resolve().parent / "templates"

    if (migrations_dir / "env.py").exists():
        print(f"[{service_name}] migrations already initialized at {migrations_dir}")
        return 0

    migrations_dir.mkdir(parents=True, exist_ok=True)
    versions_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(template_dir / "env.py", migrations_dir / "env.py")
    shutil.copy(template_dir / "script.py.mako", migrations_dir / "script.py.mako")
    (versions_dir / ".gitkeep").touch()

    print(f"[{service_name}] initialized at {migrations_dir}")
    return 0


def cmd_list() -> int:
    """列出所有微服务"""
    from common.db.migrator.config import list_services

    services = list_services()
    if not services:
        print("No services found under services/")
        return 0
    for s in services:
        print(s)
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Database migration per microservice",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("-s", "--service", help="Service name (iam, product, ...)")

    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="List all microservices")
    p_init = sub.add_parser("init", help="Initialize migrations for a service")
    p_init.add_argument("-s", "--service", required=True, dest="init_service", help="Service name")

    p_gen = sub.add_parser("generate", help="Generate migration script (autogenerate)")
    p_gen.add_argument("message", nargs="?", default="auto", help="Migration message")

    sub.add_parser("up", help="Apply all pending migrations")

    p_down = sub.add_parser("down", help="Rollback migrations")
    p_down.add_argument("steps", nargs="?", default="1", help="Steps to rollback; 'base' for full")

    sub.add_parser("history", help="Show migration history")
    sub.add_parser("current", help="Show current revision")

    args = parser.parse_args()

    if args.cmd == "list":
        return cmd_list()

    if args.cmd == "init":
        return cmd_init(args.init_service)

    # 以下命令需要 -s（从主 parser 传入）
    service = args.service
    if not service:
        parser.error(f"'{args.cmd}' requires -s/--service. Example: migrate -s iam {args.cmd}")
        return 1

    _ensure_service(service)

    def run():
        from alembic import command
        cfg = _get_alembic_config(service)

        if args.cmd == "generate":
            command.revision(cfg, message=args.message, autogenerate=True)
        elif args.cmd == "up":
            command.upgrade(cfg, "head")
        elif args.cmd == "down":
            steps = args.steps
            if steps.isdigit():
                steps = f"-{steps}"
            command.downgrade(cfg, steps)
        elif args.cmd == "history":
            command.history(cfg, verbose=True)
        elif args.cmd == "current":
            command.current(cfg, verbose=True)
        return 0

    try:
        return _run_with_service(service, run)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
