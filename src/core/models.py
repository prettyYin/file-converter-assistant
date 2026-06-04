"""数据模型定义"""
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class ConversionType(Enum):
    """转换类型枚举"""
    PDF_TO_WORD = auto()
    PDF_TO_PPT = auto()
    PDF_TO_EXCEL = auto()
    PDF_TO_LONG_IMAGE = auto()
    PDF_TO_PAGE_IMAGES = auto()
    PDF_SPLIT = auto()
    PDF_MERGE = auto()
    WORD_TO_PDF = auto()
    PPT_TO_PDF = auto()
    EXCEL_TO_PDF = auto()
    IMAGE_TO_WORD = auto()
    IMAGE_TO_EXCEL = auto()
    IMAGE_TO_PDF = auto()


# 转换类型的显示信息
CONVERSION_INFO = {
    ConversionType.PDF_TO_WORD: {
        "title": "PDF → Word",
        "description": "将PDF文件转换为可编辑的Word文档",
        "category": "pdf_to_office",
        "input_exts": [".pdf"],
        "output_ext": ".docx",
    },
    ConversionType.PDF_TO_PPT: {
        "title": "PDF → PPT",
        "description": "将PDF文件转换为演示文稿",
        "category": "pdf_to_office",
        "input_exts": [".pdf"],
        "output_ext": ".pptx",
    },
    ConversionType.PDF_TO_EXCEL: {
        "title": "PDF → Excel",
        "description": "将PDF中的表格提取到Excel",
        "category": "pdf_to_office",
        "input_exts": [".pdf"],
        "output_ext": ".xlsx",
    },
    ConversionType.PDF_TO_LONG_IMAGE: {
        "title": "PDF → 长图",
        "description": "将PDF所有页面拼接为一张长图",
        "category": "pdf_to_image",
        "input_exts": [".pdf"],
        "output_ext": ".png",
    },
    ConversionType.PDF_TO_PAGE_IMAGES: {
        "title": "PDF → 逐页图片",
        "description": "将PDF每一页导出为单独的图片",
        "category": "pdf_to_image",
        "input_exts": [".pdf"],
        "output_ext": ".png",
    },
    ConversionType.PDF_SPLIT: {
        "title": "PDF 拆分",
        "description": "将PDF按页码范围拆分为多个文件",
        "category": "pdf_edit",
        "input_exts": [".pdf"],
        "output_ext": ".pdf",
    },
    ConversionType.PDF_MERGE: {
        "title": "PDF 合并",
        "description": "将多个PDF文件合并为一个文件",
        "category": "pdf_edit",
        "input_exts": [".pdf"],
        "output_ext": ".pdf",
    },
    ConversionType.WORD_TO_PDF: {
        "title": "Word → PDF",
        "description": "将Word文档转换为PDF文件",
        "category": "office_to_pdf",
        "input_exts": [".docx", ".doc"],
        "output_ext": ".pdf",
    },
    ConversionType.PPT_TO_PDF: {
        "title": "PPT → PDF",
        "description": "将PPT演示文稿转换为PDF文件",
        "category": "office_to_pdf",
        "input_exts": [".pptx", ".ppt"],
        "output_ext": ".pdf",
    },
    ConversionType.EXCEL_TO_PDF: {
        "title": "Excel → PDF",
        "description": "将Excel表格转换为PDF文件",
        "category": "office_to_pdf",
        "input_exts": [".xlsx", ".xls"],
        "output_ext": ".pdf",
    },
    ConversionType.IMAGE_TO_WORD: {
        "title": "图片 → Word",
        "description": "识别图片中的文字并导出为Word",
        "category": "image_ocr",
        "input_exts": [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"],
        "output_ext": ".docx",
    },
    ConversionType.IMAGE_TO_EXCEL: {
        "title": "图片 → Excel",
        "description": "识别图片中的表格并导出为Excel",
        "category": "image_ocr",
        "input_exts": [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"],
        "output_ext": ".xlsx",
    },
    ConversionType.IMAGE_TO_PDF: {
        "title": "图片 → PDF",
        "description": "将一张或多张图片合并为PDF文件",
        "category": "image_ocr",
        "input_exts": [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"],
        "output_ext": ".pdf",
    },
}


@dataclass
class ConversionResult:
    """单个文件转换结果"""
    success: bool
    input_path: str
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    file_size: int = 0

    @property
    def is_success(self) -> bool:
        return self.success and self.output_path is not None


@dataclass
class ConversionOptions:
    """转换选项"""
    dpi: int = 200
    image_format: str = "png"
    language: str = "chi_sim+eng"
    preserve_images: bool = True
    preserve_tables: bool = True
    quality: str = "high"  # high / medium / low
    page_range: str = ""   # 如 "1-5,7,10-12"
