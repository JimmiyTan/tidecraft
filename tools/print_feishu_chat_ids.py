"""打印飞书机器人所在群聊的群名和 chat_id。

用途：
1. 从项目根目录 .env 读取 FEISHU_APP_ID 和 FEISHU_APP_SECRET。
2. 获取 tenant_access_token。
3. 调用飞书“获取用户或机器人所在的群列表”接口。
4. 只打印群名和 chat_id，不打印任何密钥。
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"
FEISHU_BASE_URL = "https://open.feishu.cn"
TIMEOUT_SECONDS = 10


class FeishuToolError(RuntimeError):
    """飞书临时工具错误。"""


def load_env() -> dict[str, str]:
    """读取项目根目录 .env。"""
    if not ENV_FILE.exists():
        raise FeishuToolError("未找到 .env，请先在项目根目录创建 .env。")

    values: dict[str, str] = {}
    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def post_json(path: str, payload: dict[str, Any], token: str = "") -> dict[str, Any]:
    """发送 JSON POST 请求。"""
    headers = {"Content-Type": "application/json; charset=utf-8"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(
        FEISHU_BASE_URL + path,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    return request_json(request)


def get_json(path: str, token: str, query: dict[str, Any] | None = None) -> dict[str, Any]:
    """发送 JSON GET 请求。"""
    query_string = urllib.parse.urlencode(query or {})
    url = FEISHU_BASE_URL + path
    if query_string:
        url = f"{url}?{query_string}"

    request = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}"},
        method="GET",
    )
    return request_json(request)


def request_json(request: urllib.request.Request) -> dict[str, Any]:
    """执行请求并解析 JSON 响应。"""
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise FeishuToolError(f"飞书 HTTP 请求失败：status={exc.code}, body={body}") from exc
    except urllib.error.URLError as exc:
        raise FeishuToolError(f"飞书网络请求失败：{exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise FeishuToolError("飞书响应不是合法 JSON。") from exc


def get_tenant_access_token(app_id: str, app_secret: str) -> str:
    """获取 tenant_access_token。"""
    payload = {
        "app_id": app_id,
        "app_secret": app_secret,
    }
    response = post_json("/open-apis/auth/v3/tenant_access_token/internal", payload)
    if response.get("code") != 0:
        raise FeishuToolError(
            "tenant_access_token 获取失败："
            f"code={response.get('code')}, msg={response.get('msg')}"
        )
    token = response.get("tenant_access_token", "")
    if not token:
        raise FeishuToolError("tenant_access_token 获取失败：响应中没有 token。")
    return token


def list_chats(token: str) -> list[dict[str, Any]]:
    """分页获取机器人所在群列表。"""
    chats: list[dict[str, Any]] = []
    page_token = ""
    while True:
        query = {"page_size": 100}
        if page_token:
            query["page_token"] = page_token
        response = get_json("/open-apis/im/v1/chats", token, query)
        if response.get("code") != 0:
            raise FeishuToolError(
                "获取群列表失败："
                f"code={response.get('code')}, msg={response.get('msg')}"
            )

        data = response.get("data") or {}
        chats.extend(data.get("items") or [])
        if not data.get("has_more"):
            break
        page_token = data.get("page_token", "")
        if not page_token:
            break
    return chats


def print_chats(chats: list[dict[str, Any]]) -> None:
    """打印群名和 chat_id。"""
    if not chats:
        print("未找到机器人所在群。请确认应用/机器人已加入目标群，并具备读取群列表权限。")
        return

    for chat in chats:
        chat_name = chat.get("name") or chat.get("chat_name") or "<未命名群>"
        chat_id = chat.get("chat_id") or "<缺少 chat_id>"
        print(f"{chat_name}\t{chat_id}")


def main() -> int:
    """临时脚本入口。"""
    env = load_env()
    app_id = env.get("FEISHU_APP_ID", "")
    app_secret = env.get("FEISHU_APP_SECRET", "")
    missing = [
        name
        for name, value in {
            "FEISHU_APP_ID": app_id,
            "FEISHU_APP_SECRET": app_secret,
        }.items()
        if not value
    ]
    if missing:
        raise FeishuToolError("缺少配置：" + ", ".join(missing))

    token = get_tenant_access_token(app_id, app_secret)
    chats = list_chats(token)
    print_chats(chats)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FeishuToolError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        raise SystemExit(1)
