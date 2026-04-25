"""飞书桥接服务入口。"""

import sys
from pathlib import Path

PROJECT_SRC = Path(__file__).resolve().parents[3] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from lobster_farm.feishu_bridge.app import main


if __name__ == "__main__":
    raise SystemExit(main())
