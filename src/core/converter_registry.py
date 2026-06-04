"""转换引擎注册表 — 将 ConversionType 映射到引擎类"""
from typing import Type

from src.core.models import ConversionType
from src.core.converter_base import BaseConverter


# 延迟导入引擎类，避免循环依赖
_registry: dict[ConversionType, Type[BaseConverter]] = {}


def register(conv_type: ConversionType):
    """装饰器：将引擎类注册到对应的转换类型"""
    def decorator(cls: Type[BaseConverter]):
        _registry[conv_type] = cls
        return cls
    return decorator


def get_engine(conv_type: ConversionType) -> Type[BaseConverter]:
    """获取指定转换类型的引擎类"""
    # 首次访问时触发各引擎模块的导入和注册
    _ensure_engines_loaded()
    if conv_type not in _registry:
        raise ValueError(f"未找到转换类型 {conv_type} 的引擎")
    return _registry[conv_type]


_engines_loaded = False


def _ensure_engines_loaded():
    """确保所有引擎模块已被导入（从而触发 @register 装饰器）"""
    global _engines_loaded
    if _engines_loaded:
        return
    # 导入所有引擎模块
    import src.engines.pdf_to_word        # noqa
    import src.engines.pdf_to_ppt         # noqa
    import src.engines.pdf_to_excel       # noqa
    import src.engines.pdf_to_long_image  # noqa
    import src.engines.pdf_to_page_images # noqa
    import src.engines.pdf_split          # noqa
    import src.engines.pdf_merge          # noqa
    import src.engines.word_to_pdf        # noqa
    import src.engines.ppt_to_pdf         # noqa
    import src.engines.excel_to_pdf       # noqa
    import src.engines.image_to_word      # noqa
    import src.engines.image_to_excel     # noqa
    import src.engines.image_to_pdf       # noqa
    _engines_loaded = True


def get_all_types() -> list[ConversionType]:
    """获取所有已注册的转换类型"""
    _ensure_engines_loaded()
    return list(_registry.keys())
