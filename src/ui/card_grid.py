"""卡片网格 — 3 列自适应网格布局，容纳所有转换卡片"""
from PySide6.QtWidgets import QWidget, QGridLayout, QScrollArea, QSizePolicy
from PySide6.QtCore import Qt

from src.ui.conversion_card import ConversionCard
from src.core.models import ConversionType, CONVERSION_INFO


class CardGrid(QScrollArea):
    """可滚动的卡片网格"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        # 容器
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(self.container)
        self.grid_layout.setContentsMargins(20, 12, 20, 20)
        self.grid_layout.setSpacing(14)

        self.setWidget(self.container)
        self.cards: list[ConversionCard] = []
        self._columns = 3

    def populate(self) -> None:
        """根据 CONVERSION_INFO 生成所有卡片"""
        # 清除旧卡片
        for card in self.cards:
            card.setParent(None)
        self.cards.clear()

        # 排序：按类别分组
        type_order = [
            ConversionType.PDF_TO_WORD,
            ConversionType.PDF_TO_PPT,
            ConversionType.PDF_TO_EXCEL,
            ConversionType.PDF_TO_LONG_IMAGE,
            ConversionType.PDF_TO_PAGE_IMAGES,
            ConversionType.PDF_SPLIT,
            ConversionType.PDF_MERGE,
            ConversionType.WORD_TO_PDF,
            ConversionType.PPT_TO_PDF,
            ConversionType.EXCEL_TO_PDF,
            ConversionType.IMAGE_TO_WORD,
            ConversionType.IMAGE_TO_EXCEL,
            ConversionType.IMAGE_TO_PDF,
        ]

        for idx, conv_type in enumerate(type_order):
            info = CONVERSION_INFO.get(conv_type)
            if info is None:
                continue

            card = ConversionCard(
                title=info["title"],
                description=info["description"],
            )
            card.clicked.connect(lambda ct=conv_type: self._on_card_clicked(ct))
            self.cards.append(card)

            row = idx // self._columns
            col = idx % self._columns
            self.grid_layout.addWidget(card, row, col)

        # 最后一行居中：通过添加弹性空间实现
        last_row_start = (len(self.cards) - 1) // self._columns * self._columns
        remaining = len(self.cards) - last_row_start
        if remaining < self._columns:
            # 在最后一行末尾添加弹性空间
            for col in range(remaining, self._columns):
                spacer = QWidget()
                spacer.setStyleSheet("background: transparent;")
                self.grid_layout.addWidget(spacer, (len(self.cards) - 1) // self._columns, col)

    def _on_card_clicked(self, conv_type: ConversionType) -> None:
        """卡片被点击 — 通知父窗口打开转换对话框"""
        main_window = self.window()
        if hasattr(main_window, "open_conversion_dialog"):
            main_window.open_conversion_dialog(conv_type)

    def resizeEvent(self, event) -> None:
        """窗口大小变化时调整列数"""
        width = event.size().width()
        if width < 650:
            new_cols = 2
        else:
            new_cols = 3

        if new_cols != self._columns:
            self._columns = new_cols
            self.populate()

        super().resizeEvent(event)
