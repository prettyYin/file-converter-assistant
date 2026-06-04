"""进度面板 — 显示转换进度和状态"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class ProgressPanel(QWidget):
    """转换进度面板"""

    cancelled = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVisible(False)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """设置布局"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(8)

        # 状态标签
        self.status_label = QLabel("准备转换...")
        self.status_label.setFont(QFont("Microsoft YaHei", 10))
        self.status_label.setStyleSheet("color: #2C3E50;")

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)

        # 进度文字
        self.progress_label = QLabel("0 / 0")
        self.progress_label.setStyleSheet("color: #7F8C9B; font-size: 12px;")
        self.progress_label.setAlignment(Qt.AlignRight)

        # 底部：进度文字 + 取消按钮
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        self.file_label = QLabel("")
        self.file_label.setStyleSheet("color: #7F8C9B; font-size: 11px;")

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setObjectName("secondaryBtn")
        self.cancel_btn.setFixedWidth(80)
        self.cancel_btn.clicked.connect(self._on_cancel)

        bottom_layout.addWidget(self.file_label, 1)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.cancel_btn)

        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addLayout(bottom_layout)

    def show_progress(self, show: bool = True) -> None:
        """显示/隐藏进度面板"""
        self.setVisible(show)

    def update_progress(self, current: int, total: int) -> None:
        """更新进度"""
        if total > 0:
            percent = int(current * 100 / total)
            self.progress_bar.setValue(percent)
            self.progress_label.setText(f"{current} / {total}")
            self.status_label.setText(f"正在转换... ({percent}%)")

    def set_current_file(self, filename: str) -> None:
        """设置当前处理的文件名"""
        self.file_label.setText(f"当前：{filename}")

    def set_completed(self, success_count: int, fail_count: int) -> None:
        """设置完成状态"""
        if fail_count == 0:
            self.status_label.setText(f"✅ 全部完成！共 {success_count} 个文件转换成功")
            self.status_label.setStyleSheet("color: #27AE60; font-weight: bold;")
        elif success_count == 0:
            self.status_label.setText(f"❌ 转换失败，共 {fail_count} 个文件出错")
            self.status_label.setStyleSheet("color: #E74C3C; font-weight: bold;")
        else:
            self.status_label.setText(
                f"⚠ 部分完成：{success_count} 个成功，{fail_count} 个失败"
            )
            self.status_label.setStyleSheet("color: #E67E22; font-weight: bold;")

        self.progress_bar.setValue(100)
        self.cancel_btn.setVisible(False)

    def set_error(self, message: str) -> None:
        """显示错误"""
        self.status_label.setText(f"❌ {message}")
        self.status_label.setStyleSheet("color: #E74C3C;")

    def reset(self) -> None:
        """重置进度面板"""
        self.status_label.setText("准备转换...")
        self.status_label.setStyleSheet("color: #2C3E50;")
        self.progress_bar.setValue(0)
        self.progress_label.setText("0 / 0")
        self.file_label.setText("")
        self.cancel_btn.setVisible(True)
        self.setVisible(False)

    def _on_cancel(self) -> None:
        """取消按钮点击"""
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setText("取消中...")
        self.status_label.setText("正在取消...")
        self.cancelled.emit()
