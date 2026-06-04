"""Word → PDF — 通过 COM 自动化（主路径）或 reportlab 回退"""
import os
import threading
from typing import Optional

from src.core.converter_base import BaseConverter
from src.core.converter_registry import register
from src.core.models import ConversionType


@register(ConversionType.WORD_TO_PDF)
class WordToPdfConverter(BaseConverter):
    """将 Word 文档转换为 PDF"""

    def convert(
        self,
        input_path: str,
        output_dir: str,
        options: Optional[dict] = None,
        cancel_event: Optional[threading.Event] = None,
    ) -> str:
        output_path = self._make_output_path(input_path, output_dir, ".pdf")

        # 主路径：使用 COM 自动化
        try:
            self._convert_via_com(input_path, output_path, cancel_event)
            return output_path
        except Exception as e:
            # 回退路径：尝试使用 python-docx + reportlab
            try:
                self._convert_via_reportlab(input_path, output_path, cancel_event)
                return output_path
            except Exception:
                raise RuntimeError(
                    f"Word 转 PDF 失败。请确保已安装 Microsoft Word，"
                    f"或文件未被其他程序占用。\n原始错误：{e}"
                )

    def _convert_via_com(
        self,
        input_path: str,
        output_path: str,
        cancel_event: Optional[threading.Event],
    ) -> None:
        """通过 Word COM 自动化转换"""
        import pythoncom
        import win32com.client

        pythoncom.CoInitialize()
        try:
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            word.DisplayAlerts = 0

            doc = word.Documents.Open(input_path)
            self._check_cancelled(cancel_event)

            # 17 = wdExportFormatPDF
            doc.ExportAsFixedFormat(output_path, 17)
            doc.Close()

            # 如果没有其他文档打开，退出 Word
            if word.Documents.Count == 0:
                word.Quit()
        finally:
            pythoncom.CoUninitialize()

    def _convert_via_reportlab(
        self,
        input_path: str,
        output_path: str,
        cancel_event: Optional[threading.Event],
    ) -> None:
        """通过 python-docx 读取 + reportlab 生成 PDF（回退方案）"""
        from docx import Document
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        # 尝试注册中文字体
        try:
            pdfmetrics.registerFont(TTFont("SimSun", "C:/Windows/Fonts/simsun.ttc"))
            pdfmetrics.registerFont(TTFont("SimHei", "C:/Windows/Fonts/simhei.ttf"))
            cn_font = "SimSun"
        except Exception:
            cn_font = "Helvetica"

        doc = Document(input_path)
        pdf_doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
        )

        styles = getSampleStyleSheet()
        cn_style = ParagraphStyle(
            "CNBody",
            parent=styles["Normal"],
            fontName=cn_font,
            fontSize=11,
            leading=18,
            spaceAfter=6,
        )

        story = []
        for para in doc.paragraphs:
            self._check_cancelled(cancel_event)
            text = para.text.strip()
            if text:
                # 检测标题样式
                if para.style.name.startswith("Heading"):
                    heading_style = ParagraphStyle(
                        f"Heading_{para.style.name}",
                        parent=cn_style,
                        fontSize=16 if "1" in para.style.name else 14,
                        spaceBefore=12,
                        spaceAfter=8,
                    )
                    story.append(Paragraph(text, heading_style))
                else:
                    story.append(Paragraph(text, cn_style))
            else:
                story.append(Spacer(1, 6))

        pdf_doc.build(story)
