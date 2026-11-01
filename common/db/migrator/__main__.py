"""支持 python -m common.db.migrator 调用"""
import sys

from common.db.migrator.cli import main

sys.exit(main())
