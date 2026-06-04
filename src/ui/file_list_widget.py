"""文件列表控件 — 显示已选文件，支持移除操作"""
import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QFontMetrics, QResizeEvent


class ElidedLabel(QLabel):
    """支持文本自动省略的标签，悬停显示完整文本"""

    def __init__(self, full_text: str = "", parent=None):
        super().__init__(parent)
        self._full_text = full_text
        self.setToolTip(full_text)
        self.setTextFormat(Qt.PlainText)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setMinimumWidth(40)

    def set_full_text(self, text: str) -> None:
        """设置完整文本"""
        self._full_text = text
        self.setToolTip(text)
        self._update_elided()

    def resizeEvent(self, event: QResizeEvent) -> None:
        """尺寸变化时重新计算省略文本"""
        super().resizeEvent(event)
        self._update_elided()

    def _update_elided(self) -> None:
        """根据当前宽度计算省略后的文本"""
        if not self._full_text:
            return
        fm = QFontMetrics(self.font())
        elided = fm.elidedText(self._full_text, Qt.ElideMiddle, self.width() - 4)
        self.setText(elided)


class FileListWidget(QWidget):
    """可移除的文件列表"""

    file_removed = Signal(str)  # 发送被移除的文件路径
    files_changed = Signal(list)  # 发送更新后的文件列表

    def __init__(self, parent=None):
        super().__init__(parent)
        self._files: list[str] = []

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.list_widget = QListWidget()
        self.list_widget.setMinimumHeight(80)
        self.list_widget.setMaximumHeight(200)
        self.list_widget.setStyleSheet("QListWidget { background: #FFFFFF; }")

        layout.addWidget(self.list_widget)

    # ── public API ──────────────────────────────────────────────

    def add_files(self, file_paths: list[str]) -> None:
        for path in file_paths:
            if path not in self._files:
                self._files.append(path)
                self._add_list_item(path)
        self.files_changed.emit(self._files)

    def add_file(self, file_path: str) -> None:
        self.add_files([file_path])

    def remove_file(self, file_path: str) -> None:
        if file_path in self._files:
            self._files.remove(file_path)
            self.file_removed.emit(file_path)
        self._rebuild_list()
        self.files_changed.emit(self._files)

    def clear(self) -> None:
        self._files.clear()
        self.list_widget.clear()

    # ── properties ──────────────────────────────────────────────

    @property
    def files(self) -> list[str]:
        return list(self._files)

    @property
    def file_count(self) -> int:
        return len(self._files)

    # ── internal ────────────────────────────────────────────────

    def _add_list_item(self, file_path: str) -> None:
        item = QListWidgetItem()
        item.setData(Qt.UserRole, file_path)

        row_widget = QWidget()
        row_widget.setStyleSheet("background: transparent;")
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(12, 8, 12, 8)
        row_layout.setSpacing(12)

        # ── 文件名（自动省略过长文本，悬停显示完整路径）──
        base_name = os.path.basename(file_path)
        name_label = ElidedLabel(base_name)
        name_label.setToolTip(file_path)       # 悬停显示完整路径
        name_label.setFont(QFont("Microsoft YaHei", 10))
        name_label.setStyleSheet("color: #2C3E50; background: transparent;")
        name_label.setMinimumHeight(24)

        # ── 文件大小 ──
        size_str = self._format_size(file_path)
        size_label = QLabel(size_str)
        size_label.setFont(QFont("Microsoft YaHei", 10))
        size_label.setStyleSheet("color: #A0AAB4; background: transparent;")
        size_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        size_label.setMinimumWidth(65)
        size_label.setMaximumWidth(110)
        size_label.setMinimumHeight(24)

        # ── 移除按钮 ──
        remove_btn = QPushButton("✕")
        remove_btn.setObjectName("removeBtn")
        remove_btn.setFixedSize(28, 28)
        remove_btn.setToolTip("移除文件")
        remove_btn.clicked.connect(lambda checked=False, p=file_path: self.remove_file(p))

        row_layout.addWidget(name_label, stretch=1)
        row_layout.addWidget(size_label, stretch=0)
        row_layout.addWidget(remove_btn, stretch=0)

        # 确保行高足够，文本不被纵向裁切
        row_widget.setMinimumHeight(40)
        item.setSizeHint(row_widget.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, row_widget)

    @staticmethod
    def _format_size(file_path: str) -> str:
        try:
            size_bytes = os.path.getsize(file_path)
        except OSError:
            return "—"
        if size_bytes < 1024:
            return f"{size_bytes} B"
        if size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        return f"{size_bytes / (1024 * 1024):.1f} MB"

    def _rebuild_list(self) -> None:
        self.list_widget.clear()
        for path in self._files:
            self._add_list_item(path)
