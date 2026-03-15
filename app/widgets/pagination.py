from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import pyqtSignal


class PaginationBar(QWidget):
    page_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current     = 1
        self.total_pages = 1
        self.total_rows  = 0
        self.page_size   = 50

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(16, 8, 16, 10)
        self.layout.setSpacing(4)
        self.rebuild()

    def update_state(self, current: int, total_pages: int, total_rows: int, page_size: int):
        self.current     = current
        self.total_pages = max(1, total_pages)
        self.total_rows  = total_rows
        self.page_size   = page_size
        self.rebuild()

    def rebuild(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cur  = self.current
        tot  = self.total_pages
        size = self.page_size

        start = (cur - 1) * size + 1
        end   = min(cur * size, self.total_rows)
        info = QLabel(f"Showing {start}–{end} of {self.total_rows:,} records")
        info.setObjectName("page_info")
        self.layout.addWidget(info)
        self.layout.addStretch()

        self.layout.addWidget(self.make_btn("‹", cur - 1, enabled=(cur > 1)))

        pages = self.page_range(cur, tot)
        prev  = None
        for p in pages:
            if prev is not None and p - prev > 1:
                dots = QLabel("…")
                dots.setObjectName("page_info")
                self.layout.addWidget(dots)
            self.layout.addWidget(self.make_btn(str(p), p, active=(p == cur)))
            prev = p

        self.layout.addWidget(self.make_btn("›", cur + 1, enabled=(cur < tot)))

    @staticmethod
    def page_range(cur: int, tot: int) -> list:
        pages = set()
        pages.add(1)
        pages.add(tot)
        for p in range(max(1, cur - 2), min(tot + 1, cur + 3)):
            pages.add(p)
        return sorted(pages)

    def make_btn(self, text: str, page: int, active=False, enabled=True) -> QPushButton:
        btn = QPushButton(text)
        btn.setObjectName("page_btn")
        btn.setEnabled(enabled)
        if active:
            btn.setProperty("active", "true")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        if enabled:
            btn.clicked.connect(lambda _, p=page: self.page_changed.emit(p))
        return btn
