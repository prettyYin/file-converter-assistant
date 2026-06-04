"""转换对话框 — 模态弹窗，包含文件选择、选项设置、进度显示"""
import os
import subprocess

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox,
    QLineEdit, QFileDialog, QComboBox, QCheckBox, QMessageBox,
)
from PySide6.QtCore import Qt

from src.core.models import ConversionType, CONVERSION_INFO, ConversionResult
from src.core.converter_registry import get_engine
from src.core.worker import ConversionWorker
from src.ui.drop_zone import DropZone
from src.ui.file_list_widget import FileListWidget
from src.ui.progress_panel import ProgressPanel
from src.utils.config import load_config, save_config


class ConversionDialog(QDialog):
    """转换操作对话框"""

    def __init__(self, conv_type: ConversionType, parent=None):
        super().__init__(parent)
        self.conv_type = conv_type
        self.info = CONVERSION_INFO.get(conv_type, {})
        self._worker: ConversionWorker | None = None
        self._completed_results: list[ConversionResult] = []

        self._setup_ui()
        self._load_settings()

    def _setup_ui(self) -> None:
        """构建对话框 UI"""
        self.setWindowTitle(f"文件全能转化助手 — {self.info.get('title', '')}")
        self.setMinimumSize(600, 560)
        self.resize(640, 640)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # 标题
        title_label = QLabel(self.info.get("title", ""))
        title_label.setObjectName("titleLabel")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2C3E50;")

        # 1. 文件选择区域
        file_group = QGroupBox("① 选择文件")
        file_layout = QVBoxLayout(file_group)

        allowed_exts = self.info.get("input_exts", [])
        # 提示文字保持简洁，具体格式由下方 format_label 单独展示，避免文字过长被截断
        hint = "将文件拖放至此处，或点击选择"

        self.drop_zone = DropZone(hint_text=hint, allowed_exts=allowed_exts)
        self.drop_zone.files_dropped.connect(self._on_files_added)

        self.file_list = FileListWidget()
        self.file_list.files_changed.connect(self._on_files_changed)

        file_layout.addWidget(self.drop_zone)
        file_layout.addWidget(self.file_list)

        # 2. 输出目录
        output_group = QGroupBox("② 输出目录")
        output_layout = QHBoxLayout(output_group)

        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setPlaceholderText("默认为源文件所在目录...")
        self.output_dir_edit.setReadOnly(True)

        browse_btn = QPushButton("浏览...")
        browse_btn.setObjectName("secondaryBtn")
        browse_btn.setFixedWidth(80)
        browse_btn.clicked.connect(self._browse_output_dir)

        output_layout.addWidget(self.output_dir_edit, 1)
        output_layout.addWidget(browse_btn)

        # 3. 选项区域（按转换类型动态变化）
        self.options_group = QGroupBox("③ 转换选项")
        self.options_layout = QVBoxLayout(self.options_group)
        self._build_options()

        # 4. 进度面板
        self.progress_panel = ProgressPanel()
        self.progress_panel.cancelled.connect(self._on_cancel)

        # 5. 底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.close_btn = QPushButton("关闭")
        self.close_btn.setObjectName("secondaryBtn")
        self.close_btn.clicked.connect(self.reject)

        self.convert_btn = QPushButton("开始转换")
        self.convert_btn.setEnabled(False)
        self.convert_btn.clicked.connect(self._start_conversion)

        self.open_folder_btn = QPushButton("打开输出目录")
        self.open_folder_btn.setObjectName("secondaryBtn")
        self.open_folder_btn.setVisible(False)
        self.open_folder_btn.clicked.connect(self._open_output_folder)

        button_layout.addWidget(self.open_folder_btn)
        button_layout.addWidget(self.close_btn)
        button_layout.addWidget(self.convert_btn)

        # 组装
        layout.addWidget(title_label)
        layout.addWidget(file_group)
        layout.addWidget(output_group)
        layout.addWidget(self.options_group)
        layout.addWidget(self.progress_panel)
        layout.addStretch()
        layout.addLayout(button_layout)

    def _build_options(self) -> None:
        """根据转换类型构建选项控件"""
        ct = self.conv_type

        # DPI 选项（PDF→图片相关）
        if ct in (
            ConversionType.PDF_TO_PAGE_IMAGES,
            ConversionType.PDF_TO_LONG_IMAGE,
            ConversionType.PDF_TO_PPT,
        ):
            dpi_layout = QHBoxLayout()
            dpi_label = QLabel("图片分辨率：")
            self.dpi_combo = QComboBox()
            self.dpi_combo.addItems(["72 (低)", "150 (中)", "200 (高)", "300 (超清)"])
            self.dpi_combo.setCurrentIndex(2)  # 默认 200
            dpi_layout.addWidget(dpi_label)
            dpi_layout.addWidget(self.dpi_combo)
            dpi_layout.addStretch()
            self.options_layout.addLayout(dpi_layout)

        # 图片格式选项
        if ct in (
            ConversionType.PDF_TO_PAGE_IMAGES,
            ConversionType.PDF_TO_LONG_IMAGE,
        ):
            fmt_layout = QHBoxLayout()
            fmt_label = QLabel("输出格式：")
            self.format_combo = QComboBox()
            self.format_combo.addItems(["PNG", "JPG", "TIFF", "BMP"])
            fmt_layout.addWidget(fmt_label)
            fmt_layout.addWidget(self.format_combo)
            fmt_layout.addStretch()
            self.options_layout.addLayout(fmt_layout)

        # 页码范围（PDF 拆分）
        if ct == ConversionType.PDF_SPLIT:
            range_layout = QHBoxLayout()
            range_label = QLabel("页码范围：")
            self.page_range_edit = QLineEdit()
            self.page_range_edit.setPlaceholderText("如：1-5,7,10-12（留空则每页拆分）")
            range_layout.addWidget(range_label)
            range_layout.addWidget(self.page_range_edit, 1)
            self.options_layout.addLayout(range_layout)

        # OCR 语言选择
        if ct in (ConversionType.IMAGE_TO_WORD, ConversionType.IMAGE_TO_EXCEL):
            lang_layout = QHBoxLayout()
            lang_label = QLabel("识别语言：")
            self.lang_combo = QComboBox()
            self.lang_combo.addItems([
                "chi_sim+eng (中英文)",
                "chi_sim (简体中文)",
                "chi_tra (繁体中文)",
                "eng (英文)",
                "jpn (日文)",
            ])
            lang_layout.addWidget(lang_label)
            lang_layout.addWidget(self.lang_combo)
            lang_layout.addStretch()
            self.options_layout.addLayout(lang_layout)

        # 图片预处理（OCR）
        if ct in (ConversionType.IMAGE_TO_WORD, ConversionType.IMAGE_TO_EXCEL):
            self.preprocess_check = QCheckBox("启用图像预处理（二值化、去噪）")
            self.preprocess_check.setChecked(True)
            self.options_layout.addWidget(self.preprocess_check)

        # 保留图片选项（PDF→Word）
        if ct == ConversionType.PDF_TO_WORD:
            self.preserve_images_check = QCheckBox("保留图片")
            self.preserve_images_check.setChecked(True)
            self.options_layout.addWidget(self.preserve_images_check)

        # 图片→PDF 页面大小
        if ct == ConversionType.IMAGE_TO_PDF:
            page_layout = QHBoxLayout()
            page_label = QLabel("页面大小：")
            self.page_size_combo = QComboBox()
            self.page_size_combo.addItems(["自动（匹配图片）", "A4", "Letter"])
            page_layout.addWidget(page_label)
            page_layout.addWidget(self.page_size_combo)
            page_layout.addStretch()
            self.options_layout.addLayout(page_layout)

        # 如果没有任何选项，隐藏选项组
        if self.options_layout.count() == 0:
            self.options_group.setVisible(False)

    def _load_settings(self) -> None:
        """加载保存的设置"""
        config = load_config()
        default_dir = config.get("output_dir", "")
        if default_dir:
            self.output_dir_edit.setText(default_dir)

    def _on_files_added(self, files: list[str]) -> None:
        """文件拖放或选择后添加"""
        self.file_list.add_files(files)
        self._update_convert_btn()

    def _on_files_changed(self, files: list[str]) -> None:
        """文件列表变化"""
        self._update_convert_btn()

    def _update_convert_btn(self) -> None:
        """更新转换按钮状态"""
        self.convert_btn.setEnabled(self.file_list.file_count > 0)

    def _browse_output_dir(self) -> None:
        """浏览输出目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_path:
            self.output_dir_edit.setText(dir_path)

    def _get_options(self) -> dict:
        """收集当前设置的选项"""
        options = {}
        ct = self.conv_type

        # DPI
        if hasattr(self, "dpi_combo"):
            dpi_map = {0: 72, 1: 150, 2: 200, 3: 300}
            options["dpi"] = dpi_map.get(self.dpi_combo.currentIndex(), 200)

        # 图片格式
        if hasattr(self, "format_combo"):
            options["image_format"] = self.format_combo.currentText().lower()

        # 页码范围
        if hasattr(self, "page_range_edit"):
            options["page_range"] = self.page_range_edit.text()

        # OCR 语言
        if hasattr(self, "lang_combo"):
            lang_map = {
                0: "chi_sim+eng",
                1: "chi_sim",
                2: "chi_tra",
                3: "eng",
                4: "jpn",
            }
            options["language"] = lang_map.get(self.lang_combo.currentIndex(), "chi_sim+eng")

        # 预处理
        if hasattr(self, "preprocess_check"):
            options["preprocess"] = self.preprocess_check.isChecked()

        # 保留图片
        if hasattr(self, "preserve_images_check"):
            options["preserve_images"] = self.preserve_images_check.isChecked()

        # 页面大小
        if hasattr(self, "page_size_combo"):
            page_map = {0: "auto", 1: "a4", 2: "letter"}
            options["page_size"] = page_map.get(self.page_size_combo.currentIndex(), "auto")

        # 文件列表（用于合并转换）
        if ct == ConversionType.PDF_MERGE:
            options["file_list"] = self.file_list.files

        # 图片转 PDF / PDF 合并的文件列表
        if ct == ConversionType.IMAGE_TO_PDF:
            options["file_list"] = self.file_list.files

        return options

    def _start_conversion(self) -> None:
        """开始转换"""
        files = self.file_list.files
        if not files:
            return

        # 确定输出目录
        output_dir = self.output_dir_edit.text()
        if not output_dir:
            output_dir = os.path.dirname(files[0])
        if not output_dir:
            output_dir = os.path.expanduser("~/Documents")

        # 保存输出目录设置
        save_config({"output_dir": output_dir})

        # 获取选项
        options = self._get_options()

        # 获取引擎
        engine_class = get_engine(self.conv_type)

        # 禁用控件
        self._set_controls_enabled(False)
        self.convert_btn.setVisible(False)
        self.close_btn.setEnabled(False)

        # 显示进度面板
        self.progress_panel.reset()
        self.progress_panel.show_progress(True)

        # 创建并启动工作线程
        self._worker = ConversionWorker(
            engine_class=engine_class,
            files=files,
            output_dir=output_dir,
            options=options,
        )
        self._worker.progress.connect(self._on_progress)
        self._worker.file_completed.connect(self._on_file_completed)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _on_progress(self, current: int, total: int) -> None:
        """进度更新"""
        self.progress_panel.update_progress(current, total)

    def _on_file_completed(self, result: ConversionResult) -> None:
        """单个文件完成"""
        self._completed_results.append(result)

        # 更新文件列表中的状态
        filename = os.path.basename(result.input_path)
        if result.success:
            self.progress_panel.set_current_file(f"{filename} ✅")
        else:
            self.progress_panel.set_current_file(f"{filename} ❌")

    def _on_finished(self, results: list[ConversionResult]) -> None:
        """全部完成"""
        self._completed_results = results
        self._worker = None

        success_count = sum(1 for r in results if r.success)
        fail_count = len(results) - success_count

        self.progress_panel.set_completed(success_count, fail_count)

        # 显示摘要
        if fail_count == 0:
            msg = f"🎉 全部转换完成！\n\n成功：{success_count} 个文件\n\n输出目录：{self.output_dir_edit.text() or '(源文件目录)'}"
        else:
            msg = f"转换完成（部分失败）\n\n成功：{success_count} 个\n失败：{fail_count} 个"
            for r in results:
                if not r.success:
                    msg += f"\n  - {os.path.basename(r.input_path)}: {r.error_message}"

        # 恢复控件
        self.close_btn.setEnabled(True)
        self.open_folder_btn.setVisible(True)
        self.convert_btn.setVisible(False)

    def _on_cancel(self) -> None:
        """取消转换"""
        if self._worker and self._worker.isRunning():
            self._worker.cancel()

    def _set_controls_enabled(self, enabled: bool) -> None:
        """启用/禁用控件"""
        self.drop_zone.setEnabled(enabled)
        self.file_list.setEnabled(enabled)
        self.options_group.setEnabled(enabled)

    def _open_output_folder(self) -> None:
        """打开输出目录"""
        output_dir = self.output_dir_edit.text()
        if not output_dir and self._completed_results:
            # 从第一个成功的结果获取目录
            for r in self._completed_results:
                if r.output_path:
                    output_dir = os.path.dirname(r.output_path)
                    break

        if output_dir and os.path.exists(output_dir):
            os.startfile(output_dir)
        else:
            QMessageBox.information(self, "提示", "输出目录不存在或未设置")

    def reject(self) -> None:
        """关闭对话框"""
        if self._worker and self._worker.isRunning():
            reply = QMessageBox.question(
                self,
                "确认关闭",
                "转换正在进行中，确定要取消并关闭吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.No:
                return
            self._worker.cancel()
            self._worker.wait(3000)

        super().reject()
