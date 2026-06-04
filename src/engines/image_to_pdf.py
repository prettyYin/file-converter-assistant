"""图片 → PDF"""
import os
import threading
from typing import Optional

import fitz
from PIL import Image

from src.core.converter_base import BaseConverter
from src.core.converter_registry import register
from src.core.models import ConversionType


@register(ConversionType.IMAGE_TO_PDF)
class ImageToPdfConverter(BaseConverter):
    """将一张或多张图片合并为一个 PDF 文件"""

    def convert(
        self,
        input_path: str,
        output_dir: str,
        options: Optional[dict] = None,
        cancel_event: Optional[threading.Event] = None,
    ) -> str:
        options = options or {}
        file_list = options.get("file_list", [input_path])
        page_size = options.get("page_size", "auto")  # auto / a4 / letter / original

        doc = fitz.open()

        for img_path in file_list:
            self._check_cancelled(cancel_event)

            img = Image.open(img_path)
            # 确保 RGB 模式
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")

            # 将 PIL Image 转为字节
            from io import BytesIO
            buf = BytesIO()
            img.save(buf, format="PNG")
            img_bytes = buf.getvalue()

            # 创建 PDF 页面
            if page_size == "auto":
                # 根据图片尺寸创建页面
                w_pt = img.width * 72 / 96  # 像素转点
                h_pt = img.height * 72 / 96
            elif page_size == "a4":
                w_pt, h_pt = 595, 842
            elif page_size == "letter":
                w_pt, h_pt = 612, 792
            else:
                w_pt = img.width * 72 / 96
                h_pt = img.height * 72 / 96

            page = doc.new_page(width=w_pt, height=h_pt)
            page.insert_image(
                page.rect,
                stream=img_bytes,
            )

            img.close()

        # 生成输出路径
        first_name = os.path.splitext(os.path.basename(file_list[0]))[0]
        suffix = "_combined" if len(file_list) > 1 else ""
        output_path = self._make_output_path(
            file_list[0], output_dir, ".pdf", suffix.strip("_") or None
        )
        # 由于 _make_output_path 未处理 suffix 为空的情况，手动处理
        if not suffix:
            output_path = os.path.join(output_dir, f"{first_name}.pdf")
            counter = 1
            while os.path.exists(output_path):
                output_path = os.path.join(output_dir, f"{first_name}_{counter}.pdf")
                counter += 1

        doc.save(output_path)
        doc.close()

        return output_path
