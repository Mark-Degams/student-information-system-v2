from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt


class DeleteModal(QWidget):
    ROW_H = 34
    HEADER_H = 32

    def __init__(
        self,
        parent=None,
        *,
        title="Confirm Delete",
        message="",
        affected_label="Affected Records",
        headers=None,
        rows=None,
        visible_rows=5,
        on_confirm=None,
        on_cancel=None,
        danger_label="Delete",
    ):
        super().__init__(parent)
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.setFixedWidth(520)
        self.build(title, message, affected_label, headers or [], rows or [], visible_rows, danger_label)

    def build(self, title, message, affected_label, headers, rows, visible_rows, danger_label):
        lay = QVBoxLayout(self)
        lay.setSpacing(14)
        lay.setContentsMargins(30, 28, 30, 28)

        lbl_title = QLabel(title)
        lbl_title.setObjectName("mdl_title")
        lay.addWidget(lbl_title)

        if message:
            lbl_msg = QLabel(message)
            lbl_msg.setObjectName("mdl_message")
            lbl_msg.setWordWrap(True)
            lay.addWidget(lbl_msg)

        if rows:
            lbl_affected = QLabel(affected_label)
            lbl_affected.setObjectName("mdl_lbl")
            lay.addWidget(lbl_affected)

            table = QTableWidget(len(rows), len(headers))
            table.setHorizontalHeaderLabels(headers)
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.setSelectionMode(QTableWidget.NoSelection)
            table.setFocusPolicy(Qt.NoFocus)
            table.verticalHeader().setVisible(False)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.setObjectName("delete_table")

            for r, row_data in enumerate(rows):
                for c, val in enumerate(row_data):
                    item = QTableWidgetItem(str(val))
                    item.setTextAlignment(Qt.AlignCenter)
                    table.setItem(r, c, item)
                table.setRowHeight(r, self.ROW_H)

            table.horizontalHeader().setFixedHeight(self.HEADER_H)

            visible = min(visible_rows, len(rows))
            fixed_h = self.HEADER_H + (visible * self.ROW_H) + 4
            table.setFixedHeight(fixed_h)

            lay.addWidget(table)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setObjectName("mdl_divider")
        lay.addWidget(line)

        btns = QHBoxLayout()
        btns.setSpacing(10)
        btns.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancel_btn")
        confirm_btn = QPushButton(danger_label)
        confirm_btn.setObjectName("danger_btn")
        cancel_btn.clicked.connect(self.cancel)
        confirm_btn.clicked.connect(self.confirm)
        btns.addWidget(cancel_btn)
        btns.addWidget(confirm_btn)
        lay.addLayout(btns)

    def cancel(self):
        if self.on_cancel:
            self.on_cancel()
        self.close()

    def confirm(self):
        if self.on_confirm:
            self.on_confirm()
        self.close()