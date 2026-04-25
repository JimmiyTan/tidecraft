"""统一路径处理工具。"""

from pathlib import Path


def get_project_root() -> Path:
    """返回项目根目录。"""
    return Path(__file__).resolve().parents[3]


def ensure_directory(path: Path) -> Path:
    """确保目录存在并返回该目录。"""
    path.mkdir(parents=True, exist_ok=True)
    return path


def resolve_project_path(value: str) -> Path:
    """将项目内相对路径解析为绝对路径。"""
    raw_path = Path(value)
    if raw_path.is_absolute():
        return raw_path
    return (get_project_root() / raw_path).resolve()
