"""PDF → 逐页图片"""
import os
import threading
from typing import Optional

import fitz

from src.core.converter_base import BaseConverter
from src.core.converter_registry import register
from src.core.models import ConversionType


@register(ConversionType.PDF_TO_PAGE_IMAGES)
class PdfToPageImagesConverter(BaseConverter):
    """将 PDF 每一页导出为单独的图片文件"""

    def convert(
        self,
        input_path: str,
        output_dir: str,
        options: Optional[dict] = None,
        cancel_event: Optional[threading.Event] = None,
    ) -> str:
        options = options or {}
        dpi = options.get("dpi", 200)
        fmt = options.get("image_format", "png")

        doc = fitz.open(input_path)
        base_name = os.path.splitext(os.path.basename(input_path))[0]

        # 为多页输出创建子目录
        page_dir = os.path.join(output_dir, f"{base_name}_pages")
        os.makedirs(page_dir, exist_ok=True)

        saved_files = []
        for i, page in enumerate(doc):
            self._check_cancelled(cancel_event)
            pix = page.get_pixmap(dpi=dpi)
            output_name = f"page_{i + 1:03d}.{fmt}"
            output_path = os.path.join(page_dir, output_name)
            pix.save(output_path)
            saved_files.append(output_path)

        doc.close()
        return page_dir
