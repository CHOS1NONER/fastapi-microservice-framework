"""
数据库迁移入口（仓库根目录执行）。

等价于：uv run python -m common.db.migrator ...

示例：
  uv run python scripts/migrator.py list
  uv run python scripts/migrator.py init -s iam
  uv run python scripts/migrator.py -s iam generate "init tables"
  uv run python scripts/migrator.py -s iam up
  uv run python scripts/migrator.py -s iam down 1
  uv run python scripts/migrator.py -s iam history
  uv run python scripts/migrator.py -s iam current
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from common.db.migrator.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
