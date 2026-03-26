from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

class GroupEditModal(QWidget):
    ROW_H = 34
    HEADER_H = 32

    def __init__(self, parent=None, *, title="Group Edit",
                 record_headers=None, record_rows=None,
                 fields=None, on_confirm=None, on_cancel=None,
                 cascade=None):
        super().__init__(parent)
        self.on_confirm  = on_confirm
        self.on_cancel   = on_cancel
        self.fields_cfg  = fields or []
        self.field_widgets = []
        self.cascade     = cascade
        self.setFixedWidth(520)
        self.build(title, record_headers or [], record_rows or [])

    def build(self, title, headers, rows):
        lay = QVBoxLayout(self)
        lay.setSpacing(14)
        lay.setContentsMargins(30, 28, 30, 28)

        lbl_title = QLabel(title)
        lbl_title.setObjectName("mdl_title")
        lay.addWidget(lbl_title)

        if rows:
            lbl_aff = QLabel(f"Selected Records ({len(rows)})")
            lbl_aff.setObjectName("mdl_lbl")
            lay.addWidget(lbl_aff)

            table = QTableWidget(len(rows), len(headers))
            table.setHorizontalHeaderLabels(headers)
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.setSelectionMode(QTableWidget.NoSelection)
            table.setFocusPolicy(Qt.NoFocus)
            table.verticalHeader().setVisible(False)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.horizontalHeader().setFixedHeight(self.HEADER_H)
            table.setObjectName("delete_table")
            table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

            for r, row_data in enumerate(rows):
                for c, val in enumerate(row_data):
                    item = QTableWidgetItem(str(val))
                    item.setTextAlignment(Qt.AlignCenter)
                    table.setItem(r, c, item)
                table.setRowHeight(r, self.ROW_H)

            visible = min(5, len(rows))
            table.setFixedHeight(self.HEADER_H + visible * self.ROW_H + 4)
            lay.addWidget(table)

        parent_widget = None
        child_widget  = None

        for cfg in self.fields_cfg:
            lbl = QLabel(cfg["label"])
            lbl.setObjectName("mdl_lbl")
            lay.addWidget(lbl)

            if cfg["type"] == "combo":
                w = QComboBox()
                w.setObjectName("mdl_combo")
                w.addItems(cfg["items"])
                if cfg.get("current") in cfg["items"]:
                    w.setCurrentText(cfg["current"])
                if self.cascade and cfg["key"] == self.cascade["parent_key"]:
                    parent_widget = w
                if self.cascade and cfg["key"] == self.cascade["child_key"]:
                    child_widget = w

            elif cfg["type"] == "spin":
                w = QSpinBox()
                w.setObjectName("mdl_spin")
                w.setRange(cfg.get("min", 1), cfg.get("max", 5))
                w.setValue(cfg.get("value", 1))
                w.setSuffix("  ")

            lay.addWidget(w)
            self.field_widgets.append((cfg["key"], w))

        if self.cascade and parent_widget and child_widget:
            def on_parent_changed(val, cw=child_widget):
                items = self.cascade["resolver"](val)
                cw.blockSignals(True)
                cw.clear()
                cw.addItems(items)
                cw.blockSignals(False)
            parent_widget.currentTextChanged.connect(on_parent_changed)
            on_parent_changed(parent_widget.currentText())

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setObjectName("mdl_divider")
        lay.addWidget(line)

        btns = QHBoxLayout()
        btns.setSpacing(10)
        btns.addStretch()
        cancel_btn  = QPushButton("Cancel")
        cancel_btn.setObjectName("cancel_btn")
        confirm_btn = QPushButton("Apply Changes")
        confirm_btn.setObjectName("save_btn")
        cancel_btn.clicked.connect(self.cancel)
        confirm_btn.clicked.connect(self.confirm)
        btns.addWidget(cancel_btn)
        btns.addWidget(confirm_btn)
        lay.addLayout(btns)

    def get_values(self):
        result = {}
        for key, w in self.field_widgets:
            if isinstance(w, QComboBox):
                result[key] = w.currentText()
            elif isinstance(w, QSpinBox):
                result[key] = w.value()
        return result

    def cancel(self):
        if self.on_cancel:
            self.on_cancel()
        self.close()

    def confirm(self):
        if self.on_confirm:
            self.on_confirm(self.get_values())
        self.close()