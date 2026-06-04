"""PPT → PDF — 通过 COM 自动化"""
import os
import threading
from typing import Optional

from src.core.converter_base import BaseConverter
from src.core.converter_registry import register
from src.core.models import ConversionType


@register(ConversionType.PPT_TO_PDF)
class PptToPdfConverter(BaseConverter):
    """将 PPT 演示文稿转换为 PDF"""

    def convert(
        self,
        input_path: str,
        output_dir: str,
        options: Optional[dict] = None,
        cancel_event: Optional[threading.Event] = None,
    ) -> str:
        output_path = self._make_output_path(input_path, output_dir, ".pdf")

        try:
            self._convert_via_com(input_path, output_path, cancel_event)
            return output_path
        except Exception as e:
            raise RuntimeError(
                f"PPT 转 PDF 失败。请确保已安装 Microsoft PowerPoint，"
                f"或文件未被其他程序占用。\n原始错误：{e}"
            )

    def _convert_via_com(
        self,
        input_path: str,
        output_path: str,
        cancel_event: Optional[threading.Event],
    ) -> None:
        """通过 PowerPoint COM 自动化转换"""
        import pythoncom
        import win32com.client

        pythoncom.CoInitialize()
        try:
            ppt = win32com.client.Dispatch("PowerPoint.Application")
            ppt.Visible = False

            presentation = ppt.Presentations.Open(input_path, WithWindow=False)
            self._check_cancelled(cancel_event)

            # 2 = ppFixedFormatTypePDF
            presentation.ExportAsFixedFormat(output_path, 2)
            presentation.Close()

            if ppt.Presentations.Count == 0:
                ppt.Quit()
        finally:
            pythoncom.CoUninitialize()
