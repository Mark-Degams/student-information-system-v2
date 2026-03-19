from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QEvent
from app.widgets.pagination import PaginationBar
from app.widgets.badge import badge_cell

PAGE_SIZE = 50


class TablePage(QWidget):
    HEADERS: list = []
    SORT_KEYS: list = []
    FIXED_WIDTHS: dict = {}
    FLEX_RATIOS: dict = {}
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.page     = 1
        self.sort_col = 0
        self.sort_asc = True
        self.q        = ""
        self.build_ui()

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.table = QTableWidget()
        self.table.setColumnCount(len(self.HEADERS))
        self.table.setHorizontalHeaderLabels(self.HEADERS)
        self.table.setAlternatingRowColors(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setFrameShape(QFrame.NoFrame)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(46)

        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Fixed)
        header.setSortIndicatorShown(True)
        header.setSortIndicator(self.sort_col, Qt.AscendingOrder)
        header.sectionClicked.connect(self.on_header_click)
        header.installEventFilter(self)
        header.viewport().setCursor(Qt.PointingHandCursor)

        self.refresh_columns()

        self.pagination = PaginationBar()
        self.pagination.page_changed.connect(self.go_page)

        root.addWidget(self.table, 1)
        root.addWidget(self.pagination)

    def refresh_columns(self):
        for col, w in self.FIXED_WIDTHS.items():
            self.table.setColumnWidth(col, w)
        if self.FLEX_RATIOS:
            fixed_total = sum(self.FIXED_WIDTHS.values())
            available = self.table.viewport().width() - fixed_total
            for col, ratio in self.FLEX_RATIOS.items():
                self.table.setColumnWidth(col, max(60, int(available * ratio)))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.refresh_columns()
        if getattr(self, "overlay", None):
            self.overlay.setGeometry(0, 0, self.width(), self.height())

    def search(self, q: str):
        self.q    = q
        self.page = 1
        self.load()

    def load(self):
        sort_key = self.SORT_KEYS[min(self.sort_col, len(self.SORT_KEYS) - 1)]
        offset   = (self.page - 1) * PAGE_SIZE
        rows, total = self.fetch(self.q, sort_key, self.sort_asc, PAGE_SIZE, offset)

        total_pages = max(1, -(-total // PAGE_SIZE))

        self.table.setRowCount(len(rows))
        for i, record in enumerate(rows):
            self.populate_row(i, record)

        self.pagination.update_state(self.page, total_pages, total, PAGE_SIZE)

    def set_text(self, row: int, col: int, text: str, align=Qt.AlignLeft | Qt.AlignVCenter):
        item = QTableWidgetItem(str(text))
        item.setTextAlignment(align)
        self.table.setItem(row, col, item)

    def set_badge(self, row: int, col: int, text: str, college_code: str = None):
        self.table.setCellWidget(row, col, badge_cell(text, college_code))

    def set_actions(self, row: int, on_edit, on_delete):
        w   = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(6, 4, 6, 4)
        lay.setSpacing(6)

        edit_btn = QPushButton("Edit")
        edit_btn.setObjectName("edit_btn")
        edit_btn.setFixedHeight(28)
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.clicked.connect(on_edit)

        del_btn = QPushButton("Delete")
        del_btn.setObjectName("del_btn")
        del_btn.setFixedHeight(28)
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.clicked.connect(on_delete)

        lay.addWidget(edit_btn)
        lay.addWidget(del_btn)
        lay.addStretch()
        self.table.setCellWidget(row, self.table.columnCount() - 1, w)

    def on_header_click(self, col_idx: int):
        exc_cols = ["Actions", "Students", "Programs"]
        if self.HEADERS[col_idx] in exc_cols:
            order = Qt.AscendingOrder if self.sort_asc else Qt.DescendingOrder
            self.table.horizontalHeader().setSortIndicator(self.sort_col, order)
            return
        
        if col_idx == self.sort_col:
            self.sort_asc = not self.sort_asc
        else:
            self.sort_col = col_idx
            self.sort_asc = True
        
        order = Qt.AscendingOrder if self.sort_asc else Qt.DescendingOrder
        self.table.horizontalHeader().setSortIndicator(self.sort_col, order)

        self.page = 1
        self.load()

    def go_page(self, page: int):
        self.page = page
        self.load()

    def eventFilter(self, obj, event):
        exc_cols = ["Actions", "Students", "Programs"]
        if obj is self.table.horizontalHeader().viewport():
            if event.type() == QEvent.MouseMove:
                self.table.horizontalHeader().viewport().setCursor(Qt.PointingHandCursor)
        if obj is self.table.horizontalHeader() and event.type() in (QEvent.MouseButtonPress, QEvent.MouseButtonRelease):
            col = obj.logicalIndexAt(event.pos())
            if col >= 0 and col < len(self.HEADERS):
                if self.HEADERS[col] in exc_cols:
                    return True
        return super().eventFilter(obj, event)

    def fetch(self, q, sort_key, asc, limit, offset):
        raise NotImplementedError

    def populate_row(self, row_idx: int, record: dict):
        raise NotImplementedError

    def add_new(self):
        raise NotImplementedError