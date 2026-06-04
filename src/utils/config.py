"""配置管理 — JSON 配置文件读写"""
import json
import os
import sys
from typing import Any

DEFAULT_CONFIG = {
    "output_dir": "",
    "default_dpi": 200,
    "default_image_format": "png",
    "ocr_language": "chi_sim+eng",
    "theme": "light",
    "last_conversion_type": None,
}


def _config_path() -> str:
    """配置文件路径：打包后写到 exe 同目录，开发时写到项目根目录"""
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, "config.json")


CONFIG_PATH = _config_path()


def load_config() -> dict[str, Any]:
    """加载配置，如果文件不存在则返回默认配置"""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
            # 合并默认值，确保所有键存在
            merged = {**DEFAULT_CONFIG, **config}
            return merged
        except (json.JSONDecodeError, IOError):
            pass
    return dict(DEFAULT_CONFIG)


def save_config(config: dict[str, Any]) -> None:
    """保存配置到文件"""
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except IOError:
        pass


def get(key: str, default: Any = None) -> Any:
    """获取单个配置项"""
    config = load_config()
    return config.get(key, default)


def set_(key: str, value: Any) -> None:
    """设置单个配置项并保存"""
    config = load_config()
    config[key] = value
    save_config(config)
