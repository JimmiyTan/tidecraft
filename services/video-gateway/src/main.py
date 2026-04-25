"""视频网关服务入口。"""

import sys
from pathlib import Path

PROJECT_SRC = Path(__file__).resolve().parents[3] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from lobster_farm.video_gateway.app import main


if __name__ == "__main__":
    raise SystemExit(main())
