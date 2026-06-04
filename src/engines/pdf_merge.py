"""PDF 合并"""
import os
import threading
from typing import Optional

import fitz

from src.core.converter_base import BaseConverter
from src.core.converter_registry import register
from src.core.models import ConversionType


@register(ConversionType.PDF_MERGE)
class PdfMergeConverter(BaseConverter):
    """将多个 PDF 文件合并为一个 PDF"""

    def convert(
        self,
        input_path: str,
        output_dir: str,
        options: Optional[dict] = None,
        cancel_event: Optional[threading.Event] = None,
    ) -> str:
        # 对于合并，input_path 实际上是文件列表的 JSON 字符串
        # 由对话框传入文件列表
        options = options or {}
        file_list = options.get("file_list", [input_path])

        if len(file_list) < 2:
            raise ValueError("请选择至少两个 PDF 文件进行合并")

        merged = fitz.open()

        for file_path in file_list:
            self._check_cancelled(cancel_event)
            src = fitz.open(file_path)
            merged.insert_pdf(src)
            src.close()

        # 使用第一个文件名生成输出名
        first_name = os.path.splitext(os.path.basename(file_list[0]))[0]
        output_path = os.path.join(output_dir, f"{first_name}_merged.pdf")

        # 处理重名
        counter = 1
        while os.path.exists(output_path):
            output_path = os.path.join(
                output_dir, f"{first_name}_merged_{counter}.pdf"
            )
            counter += 1

        merged.save(output_path)
        merged.close()

        return output_path
