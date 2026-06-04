"""Toast 通知 — 非阻塞式右下角通知"""
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, Property
from PySide6.QtGui import QFont


class ToastWidget(QWidget):
    """浮动 Toast 通知"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.ToolTip | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setFixedWidth(320)

        self._setup_ui()
        self.hide()

        # 自动隐藏定时器
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self._fade_out)

    def _setup_ui(self) -> None:
        """设置布局"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.container = QWidget()
        self.container.setObjectName("toastContainer")
        self.container.setStyleSheet("""
            QWidget#toastContainer {
                background-color: #2C3E50;
                border-radius: 10px;
            }
        """)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(16, 12, 16, 12)

        self.message_label = QLabel()
        self.message_label.setFont(QFont("Microsoft YaHei", 10))
        self.message_label.setStyleSheet("color: #FFFFFF; background: transparent;")
        self.message_label.setWordWrap(True)

        container_layout.addWidget(self.message_label)
        layout.addWidget(self.container)

    def show_message(self, message: str, duration: int = 3000, success: bool = True) -> None:
        """显示通知消息"""
        self.message_label.setText(message)

        # 根据类型设置颜色
        color = "#27AE60" if success else "#E74C3C"
        self.container.setStyleSheet(f"""
            QWidget#toastContainer {{
                background-color: #2C3E50;
                border-left: 3px solid {color};
                border-radius: 10px;
            }}
        """)

        # 定位到父窗口右下角
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.right() - self.width() - 20
            y = parent_rect.bottom() - self.height() - 40
            self.move(x, y)

        self._fade_in()
        self._hide_timer.start(duration)

    def _fade_in(self) -> None:
        """淡入动画"""
        self.show()
        self.raise_()

    def _fade_out(self) -> None:
        """淡出动画"""
        self.hide()
