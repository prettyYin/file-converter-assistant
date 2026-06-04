"""应用初始化 — 创建 QApplication、加载主题、启动主窗口"""
import sys
import os

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import Qt

from src.utils.logger import setup_logger


def resource_base_dir() -> str:
    """获取资源根目录，兼容开发环境与 PyInstaller 打包环境"""
    if getattr(sys, "frozen", False):
        # PyInstaller 打包后，资源解压到 sys._MEIPASS
        return sys._MEIPASS  # type: ignore[attr-defined]
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_stylesheet(app: QApplication) -> None:
    """加载 QSS 主题样式表"""
    qss_path = os.path.join(resource_base_dir(), "assets", "styles", "theme.qss")

    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            qss = f.read()
        app.setStyleSheet(qss)


def main():
    """应用入口"""
    # 初始化日志
    logger = setup_logger()
    logger.info("文件全能转化助手 启动")

    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("文件全能转化助手")
    app.setOrganizationName("FileConverter")

    # 设置应用图标
    icon_path = os.path.join(resource_base_dir(), "assets", "icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # 设置默认字体
    font = QFont("Microsoft YaHei", 10)
    font.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(font)

    # 启用高 DPI 支持
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # 加载 QSS 主题
    load_stylesheet(app)

    # 导入并显示主窗口
    from src.main_window import MainWindow
    window = MainWindow()
    window.show()

    logger.info("主窗口已显示")

    sys.exit(app.exec())
