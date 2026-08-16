"""客户演示站点本地服务入口。"""

import argparse
import sys
import threading
import webbrowser
from http.server import ThreadingHTTPServer
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROJECT_SRC = PROJECT_ROOT / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from lobster_farm.common.config import load_app_config
from lobster_farm.customer_demo_web import (
    CustomerDemoApplication,
    build_customer_demo_handler,
)
from lobster_farm.demo import assert_demo_safe_config


def build_parser() -> argparse.ArgumentParser:
    """构建本地客户演示服务参数。"""
    parser = argparse.ArgumentParser(description="lobster-farm 客户演示站点")
    parser.add_argument("--port", type=int, default=8765, help="本地监听端口")
    parser.add_argument("--open", action="store_true", help="启动后打开默认浏览器")
    return parser


def main() -> int:
    """仅监听本机地址并启动客户演示页面。"""
    args = build_parser().parse_args()
    if not 1024 <= args.port <= 65535:
        raise SystemExit("端口必须在 1024 到 65535 之间。")

    config = load_app_config(PROJECT_ROOT / ".env.example")
    assert_demo_safe_config(config)
    application = CustomerDemoApplication(
        project_root=PROJECT_ROOT,
        static_dir=PROJECT_ROOT / "apps" / "customer-demo",
        config=config,
    )
    handler = build_customer_demo_handler(application)
    url = f"http://127.0.0.1:{args.port}"
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    except OSError:
        print(f"客户演示启动失败：本地端口 {args.port} 不可用。", file=sys.stderr)
        return 1

    if args.open:
        threading.Timer(0.7, lambda: webbrowser.open(url)).start()

    print("lobster-farm 客户演示已启动")
    print(f"访问地址：{url}")
    print("安全模式：dry-run / Feishu dry-run / Video mock")
    print("按 Ctrl+C 停止服务。")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n客户演示服务已停止。")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
