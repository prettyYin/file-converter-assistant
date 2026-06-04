"""拖放区域 — 支持文件拖放的醒目区域"""
import os

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QFont


class DropZone(QFrame):
    """文件拖放目标区域"""

    files_dropped = Signal(list)  # 发送文件路径列表

    def __init__(self, hint_text: str = "", allowed_exts: list[str] = None, parent=None):
        super().__init__(parent)
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        self.setMinimumHeight(132)
        # 不设最大高度，让内容自适应；用 sizePolicy 控制伸缩
        from PySide6.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.allowed_exts = allowed_exts or []
        self._hint_text = hint_text or "将文件拖放至此处，或点击选择"

        self._setup_ui()
        self._apply_style()

    def _setup_ui(self) -> None:
        """设置布局"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(6)
        layout.addStretch(1)

        # 上传图标（使用 Unicode 字符代替图标文件）
        self.icon_label = QLabel("📁")
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setFont(QFont("Segoe UI Emoji", 22))
        self.icon_label.setStyleSheet("background: transparent;")
        self.icon_label.setFixedHeight(34)

        # 提示文字
        self.hint_label = QLabel(self._hint_text)
        self.hint_label.setObjectName("dropHintLabel")
        self.hint_label.setAlignment(Qt.AlignCenter)
        self.hint_label.setWordWrap(True)
        self.hint_label.setStyleSheet("background: transparent;")

        # 格式提示
        if self.allowed_exts:
            ext_str = "、".join(self.allowed_exts)
            self.format_label = QLabel(f"支持格式：{ext_str}")
        else:
            self.format_label = QLabel("支持所有文件格式")
        self.format_label.setAlignment(Qt.AlignCenter)
        self.format_label.setWordWrap(True)
        self.format_label.setStyleSheet("color: #A0AAB4; font-size: 11px; background: transparent;")

        layout.addWidget(self.icon_label)
        layout.addWidget(self.hint_label)
        layout.addWidget(self.format_label)
        layout.addStretch(1)

    def _apply_style(self) -> None:
        """应用虚线边框样式"""
        self.setStyleSheet("""
            QFrame#dropZone {
                background-color: #FAFBFD;
                border: 2px dashed #C4CDD5;
                border-radius: 12px;
            }
            QFrame#dropZone:hover {
                border-color: #4A90D9;
                background-color: #F0F5FB;
            }
        """)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """拖入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QFrame#dropZone {
                    background-color: #E8F0FB;
                    border: 2px solid #4A90D9;
                    border-radius: 12px;
                }
            """)

    def dragLeaveEvent(self, event) -> None:
        """拖出事件"""
        self._apply_style()

    def dropEvent(self, event: QDropEvent) -> None:
        """放下事件"""
        self._apply_style()
        files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                # 检查扩展名过滤
                if self.allowed_exts:
                    ext = os.path.splitext(file_path)[1].lower()
                    if ext not in self.allowed_exts:
                        continue
                files.append(file_path)

        if files:
            self.files_dropped.emit(files)

    def mousePressEvent(self, event) -> None:
        """点击时触发文件选择"""
        from PySide6.QtWidgets import QFileDialog

        if self.allowed_exts:
            filter_str = "支持的文件 ("
            filter_str += " ".join(f"*{ext}" for ext in self.allowed_exts)
            filter_str += ")"
        else:
            filter_str = "所有文件 (*.*)"

        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择文件",
            "",
            filter_str,
        )
        if files:
            self.files_dropped.emit(files)
