"""转换卡片控件 — 单张可点击的转换类型卡片"""
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QFont, QEnterEvent, QMouseEvent, QPainter, QColor


class ConversionCard(QFrame):
    """可点击的转换类型卡片"""

    clicked = Signal()

    def __init__(
        self,
        title: str,
        description: str,
        icon_path: str = "",
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("conversionCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumSize(QSize(200, 140))
        self.setMaximumSize(QSize(280, 160))

        self._setup_ui(title, description, icon_path)
        self._apply_style()

    def _setup_ui(self, title: str, description: str, icon_path: str) -> None:
        """设置卡片内部布局"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        # 图标
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(36, 36)
        self.icon_label.setAlignment(Qt.AlignCenter)
        if icon_path:
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                self.icon_label.setPixmap(
                    pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )

        # 标题
        self.title_label = QLabel(title)
        self.title_label.setObjectName("cardTitle")
        self.title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        self.title_label.setStyleSheet("color: #2C3E50; background: transparent;")

        # 描述
        self.desc_label = QLabel(description)
        self.desc_label.setObjectName("cardDesc")
        self.desc_label.setWordWrap(True)
        self.desc_label.setFont(QFont("Microsoft YaHei", 9))
        self.desc_label.setStyleSheet("color: #7F8C9B; background: transparent;")

        # 箭头指示
        self.arrow_label = QLabel("→")
        self.arrow_label.setAlignment(Qt.AlignRight)
        self.arrow_label.setStyleSheet("color: #4A90D9; font-size: 16px; font-weight: bold; background: transparent;")

        layout.addWidget(self.icon_label)
        layout.addWidget(self.title_label)
        layout.addWidget(self.desc_label)
        layout.addStretch()
        layout.addWidget(self.arrow_label)

    def _apply_style(self) -> None:
        """应用卡片样式"""
        self.setStyleSheet("""
            QFrame#conversionCard {
                background-color: #FFFFFF;
                border: 1.5px solid #E8ECF0;
                border-radius: 12px;
                padding: 4px;
            }
            QFrame#conversionCard:hover {
                border-color: #4A90D9;
                background-color: #FAFBFD;
            }
        """)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """点击事件"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def enterEvent(self, event: QEnterEvent) -> None:
        """鼠标进入 — 微缩放效果"""
        self.setGraphicsEffect(None)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        super().leaveEvent(event)
