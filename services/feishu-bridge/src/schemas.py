"""兼容层：保留旧路径，转发到统一包实现。"""

import sys
from pathlib import Path

PROJECT_SRC = Path(__file__).resolve().parents[3] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from lobster_farm.feishu_bridge.schemas import ReviewItem, ReviewMessageRequest, ReviewMessageResponse
