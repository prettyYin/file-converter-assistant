"""OCR 核心 — Tesseract 初始化和共享逻辑"""
import os
import sys
import pytesseract


def init_tesseract() -> None:
    """初始化 Tesseract OCR，优先使用捆绑的便携版"""
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS  # type: ignore
    else:
        base_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )

    tesseract_exe = os.path.join(base_dir, "assets", "tesseract", "tesseract.exe")
    tessdata_dir = os.path.join(base_dir, "assets", "tesseract", "tessdata")

    if os.path.exists(tesseract_exe):
        pytesseract.pytesseract.tesseract_cmd = tesseract_exe
        if os.path.exists(tessdata_dir):
            os.environ["TESSDATA_PREFIX"] = tessdata_dir


def get_available_languages() -> list[str]:
    """获取可用的 OCR 语言列表"""
    try:
        langs = pytesseract.get_languages()
        return langs
    except Exception:
        return ["eng"]


# 模块加载时初始化
try:
    init_tesseract()
except Exception:
    pass
