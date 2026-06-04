"""PDF 拆分"""
import os
import re
import threading
from typing import Optional

import fitz

from src.core.converter_base import BaseConverter
from src.core.converter_registry import register
from src.core.models import ConversionType


@register(ConversionType.PDF_SPLIT)
class PdfSplitConverter(BaseConverter):
    """将 PDF 按页码范围拆分为多个文件"""

    def convert(
        self,
        input_path: str,
        output_dir: str,
        options: Optional[dict] = None,
        cancel_event: Optional[threading.Event] = None,
    ) -> str:
        options = options or {}
        page_range = options.get("page_range", "")

        doc = fitz.open(input_path)
        total_pages = len(doc)

        # 解析页码范围
        ranges = self._parse_page_ranges(page_range, total_pages)

        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_files = []

        for idx, (start, end) in enumerate(ranges):
            self._check_cancelled(cancel_event)
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=start, to_page=end)
            output_path = self._make_output_path(
                input_path, output_dir, ".pdf", f"part_{idx + 1}"
            )
            new_doc.save(output_path)
            new_doc.close()
            output_files.append(output_path)

        doc.close()

        if not output_files:
            raise ValueError("未生成任何拆分文件，请检查页码范围")

        return output_dir

    def _parse_page_ranges(
        self, range_str: str, total_pages: int
    ) -> list[tuple[int, int]]:
        """解析页码范围字符串，返回 [(start, end), ...]（0-based）"""
        if not range_str.strip():
            # 每页拆分为独立文件
            return [(i, i) for i in range(total_pages)]

        ranges = []
        parts = re.split(r"[;,，]\s*", range_str)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                a, b = part.split("-", 1)
                start = int(a.strip()) - 1
                end = int(b.strip()) - 1
            else:
                start = end = int(part) - 1

            # 边界检查
            start = max(0, min(start, total_pages - 1))
            end = max(0, min(end, total_pages - 1))
            if start <= end:
                ranges.append((start, end))

        return ranges if ranges else [(0, total_pages - 1)]
