"""
工具函数
"""
from datetime import datetime
from typing import Any, Dict
import os


def format_currency(amount: float) -> str:
    """格式化金额"""
    return f"¥{amount:,.2f}"


def safe_get(data: Dict, key: str, default: Any = None) -> Any:
    """安全获取字典值"""
    return data.get(key, default)


def ensure_dir(directory: str) -> None:
    """确保目录存在"""
    os.makedirs(directory, exist_ok=True)


def get_timestamp() -> str:
    """获取当前时间戳字符串"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def validate_file_extension(filename: str, allowed_extensions: list) -> bool:
    """验证文件扩展名"""
    return any(filename.lower().endswith(ext) for ext in allowed_extensions)


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


