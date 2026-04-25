"""飞书消息 adapter 注册入口。"""

from lobster_farm.common.config import AppConfig
from lobster_farm.feishu_bridge.adapters.base import FeishuAdapter
from lobster_farm.feishu_bridge.adapters.dry_run import DryRunFeishuAdapter
from lobster_farm.feishu_bridge.adapters.real import RealFeishuAdapter


def get_feishu_adapter(config: AppConfig) -> FeishuAdapter:
    """按配置返回飞书 adapter。"""
    adapters: dict[str, FeishuAdapter] = {
        "dry-run": DryRunFeishuAdapter(),
        "real": RealFeishuAdapter(config),
    }
    return adapters[config.feishu_adapter]
