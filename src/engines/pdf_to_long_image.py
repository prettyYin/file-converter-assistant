"""PDF → 长图（所有页面垂直拼接）"""
import os
import threading
from typing import Optional

import fitz
from PIL import Image

from src.core.converter_base import BaseConverter
from src.core.converter_registry import register
from src.core.models import ConversionType


@register(ConversionType.PDF_TO_LONG_IMAGE)
class PdfToLongImageConverter(BaseConverter):
    """将 PDF 所有页面垂直拼接为一张长图"""

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
        gap = options.get("page_gap", 4)  # 页间距（像素）

        doc = fitz.open(input_path)
        page_images = []

        # 逐页渲染为 PIL Image
        max_width = 0
        for page in doc:
            self._check_cancelled(cancel_event)
            pix = page.get_pixmap(dpi=dpi)
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            page_images.append(img)
            if pix.width > max_width:
                max_width = pix.width

        doc.close()

        if not page_images:
            raise ValueError("PDF 文件无页面")

        # 计算总高度
        total_height = sum(img.height for img in page_images) + gap * (len(page_images) - 1)

        # 创建长图
        long_image = Image.new("RGB", (max_width, total_height), "white")
        y_offset = 0
        for img in page_images:
            self._check_cancelled(cancel_event)
            # 如果图片宽度小于最大宽度，居中放置
            x_offset = (max_width - img.width) // 2
            long_image.paste(img, (x_offset, y_offset))
            y_offset += img.height + gap

        # 保存
        output_path = self._make_output_path(input_path, output_dir, f".{fmt}")
        save_format = "JPEG" if fmt.lower() == "jpg" else fmt.upper()
        save_kwargs = {}
        if save_format == "JPEG":
            save_kwargs["quality"] = 95
        long_image.save(output_path, format=save_format, **save_kwargs)

        return output_path
