"""主窗口 — 包含菜单栏、卡片网格、拖放区、状态栏"""
import os

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QMenuBar, QMenu,
    QStatusBar, QMessageBox, QLabel,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QFont

from src.core.models import ConversionType
from src.ui.card_grid import CardGrid
from src.ui.conversion_dialog import ConversionDialog


class MainWindow(QMainWindow):
    """文件全能转化助手 主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("文件全能转化助手")
        self.setMinimumSize(800, 600)
        self.resize(960, 700)

        self._setup_menu_bar()
        self._setup_central_widget()
        self._setup_status_bar()

        # 应用样式
        self.setStyleSheet("QMainWindow { background-color: #F5F6FA; }")

    def _setup_menu_bar(self) -> None:
        """设置菜单栏"""
        menu_bar = self.menuBar()

        # 文件菜单
        file_menu = menu_bar.addMenu("文件(&F)")

        open_action = QAction("打开文件...", self)
        open_action.triggered.connect(self._on_open_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction("退出(&X)", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 设置菜单
        settings_menu = menu_bar.addMenu("设置(&S)")

        output_dir_action = QAction("默认输出目录...", self)
        output_dir_action.triggered.connect(self._on_set_output_dir)
        settings_menu.addAction(output_dir_action)

        # 帮助菜单
        help_menu = menu_bar.addMenu("帮助(&H)")

        about_action = QAction("关于...", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _setup_central_widget(self) -> None:
        """设置中央控件"""
        central = QWidget()
        central.setStyleSheet("background-color: #F5F6FA;")
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 标题区域
        title_container = QWidget()
        title_container.setStyleSheet("background-color: #FFFFFF;")
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(24, 16, 24, 12)
        title_layout.setSpacing(4)

        app_title = QLabel("文件全能转化助手")
        app_title.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))
        app_title.setStyleSheet("color: #2C3E50; background: transparent;")

        app_subtitle = QLabel("支持 PDF、Word、PPT、Excel、图片等格式的全能转换工具")
        app_subtitle.setStyleSheet("color: #7F8C9B; font-size: 12px; background: transparent;")

        title_layout.addWidget(app_title)
        title_layout.addWidget(app_subtitle)

        # 卡片网格
        self.card_grid = CardGrid()
        self.card_grid.populate()

        layout.addWidget(title_container)
        layout.addWidget(self.card_grid, 1)

        self.setCentralWidget(central)

    def _setup_status_bar(self) -> None:
        """设置状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪 — 点击任意转换卡片开始")

    def open_conversion_dialog(self, conv_type: ConversionType) -> None:
        """打开转换对话框（由 CardGrid 调用）"""
        dialog = ConversionDialog(conv_type, self)
        dialog.exec()

        # 更新状态栏
        self.status_bar.showMessage("就绪 — 点击任意转换卡片开始")

    def _on_open_file(self) -> None:
        """打开文件菜单项 — 提示用户选择转换类型"""
        QMessageBox.information(
            self,
            "提示",
            "请点击下方卡片选择需要进行的转换类型，然后在弹出的对话框中添加文件。"
        )

    def _on_set_output_dir(self) -> None:
        """设置默认输出目录"""
        from PySide6.QtWidgets import QFileDialog
        from src.utils.config import load_config, save_config

        config = load_config()
        current_dir = config.get("output_dir", "")

        dir_path = QFileDialog.getExistingDirectory(self, "选择默认输出目录", current_dir)
        if dir_path:
            save_config({"output_dir": dir_path})
            QMessageBox.information(
                self,
                "设置成功",
                f"默认输出目录已设置为：\n{dir_path}"
            )

    def _on_about(self) -> None:
        """关于对话框"""
        QMessageBox.about(
            self,
            "关于 文件全能转化助手",
            "<h3>文件全能转化助手</h3>"
            "<p>版本 1.0.0</p>"
            "<p>一款全能文件格式转换工具，支持以下转换：</p>"
            "<ul>"
            "<li>PDF → Word / PPT / Excel / 长图 / 逐页图片</li>"
            "<li>PDF 拆分 / 合并</li>"
            "<li>Word / PPT / Excel → PDF</li>"
            "<li>图片 → Word / Excel / PDF（OCR 识别）</li>"
            "</ul>"
            "<p>基于 PyMuPDF、Tesseract OCR、python-docx 等开源技术构建。</p>"
        )
