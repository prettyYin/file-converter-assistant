"""Excel → PDF — 通过 COM 自动化"""
import os
import threading
from typing import Optional

from src.core.converter_base import BaseConverter
from src.core.converter_registry import register
from src.core.models import ConversionType


@register(ConversionType.EXCEL_TO_PDF)
class ExcelToPdfConverter(BaseConverter):
    """将 Excel 表格转换为 PDF"""

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
                f"Excel 转 PDF 失败。请确保已安装 Microsoft Excel，"
                f"或文件未被其他程序占用。\n原始错误：{e}"
            )

    def _convert_via_com(
        self,
        input_path: str,
        output_path: str,
        cancel_event: Optional[threading.Event],
    ) -> None:
        """通过 Excel COM 自动化转换"""
        import pythoncom
        import win32com.client

        pythoncom.CoInitialize()
        try:
            excel = win32com.client.Dispatch("Excel.Application")
            excel.Visible = False
            excel.DisplayAlerts = False

            wb = excel.Workbooks.Open(input_path)
            self._check_cancelled(cancel_event)

            # 0 = xlTypePDF
            wb.ExportAsFixedFormat(0, output_path)
            wb.Close()

            if excel.Workbooks.Count == 0:
                excel.Quit()
        finally:
            pythoncom.CoUninitialize()
