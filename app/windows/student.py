from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from app.widgets.table import TablePage
from app.widgets.modal_overlay import ModalOverlay
from app.modals.student_modal import StudentModal
import app.database as db


class StudentWin(TablePage):
    HEADERS = ["ID Number", "First Name", "Last Name", "Course", "Year", "Gender", "Actions"]
    SORT_KEYS = ["id", "firstname", "lastname", "course", "year", "gender", "Actions"]
    FIXED_WIDTHS = {0: 110, 4: 70, 5: 85, 6: 150}
    FLEX_RATIOS = {1: 0.30, 2: 0.35, 3: 0.35} 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.overlay = None
        self.load()

    def open_modal(self, modal_widget: StudentModal):
        self.close_modal()            
        self.overlay = ModalOverlay(self, modal_widget)
        self.overlay.setGeometry(0, 0, self.width(), self.height())

    def close_modal(self):
        if self.overlay:
            self.overlay.close_overlay()
            self.overlay = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        fixed_total = sum(self.FIXED_WIDTHS.values())
        available = self.table.viewport().width() - fixed_total
        for col, ratio in self.FLEX_RATIOS.items():
            self.table.setColumnWidth(col, max(60, int(available * ratio)))
        if self.overlay:
            self.overlay.setGeometry(0, 0, self.width(), self.height())

    def set_column_widths(self):
        for col, w in self.FIXED_WIDTHS.items():
            self.table.setColumnWidth(col, w)

    def fetch(self, q, sort_key, asc, limit, offset):
        return db.student_list(q, sort_key, asc, limit, offset)

    def populate_row(self, row_idx, rec):
        self.set_text(row_idx, 0, rec["id"])
        self.set_text(row_idx, 1, rec["firstname"])
        self.set_text(row_idx, 2, rec["lastname"])
        self.set_badge(row_idx, 3, rec["course"], rec.get("college_code"))
        self.set_text(row_idx, 4, str(rec["year"]), Qt.AlignCenter | Qt.AlignVCenter)
        self.set_text(row_idx, 5, rec["gender"])
        self.set_actions(
            row_idx,
            on_edit=lambda _, r=rec: self.edit(r),
            on_delete=lambda _, r=rec: self.delete(r),
        )

    def delete(self, rec):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete student '{rec['firstname']} {rec['lastname']}' ({rec['id']})?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        try:
            db.student_delete(rec["id"])
            self.load()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def edit(self, rec):
        def on_save(data):
            try:
                db.student_update(*data)
                self.close_modal()
                self.load()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

        mdl = StudentModal(
            sid=rec["id"], firstname=rec["firstname"], lastname=rec["lastname"],
            course=rec["course"], year=rec["year"], gender=rec["gender"],
            edit_mode=True, on_save=on_save, on_cancel=self.close_modal,
        )
        self.open_modal(mdl)

    def add_new(self):
        def on_save(data):
            try:
                db.student_add(*data)
                self.close_modal()
                self.load()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

        mdl = StudentModal(
            on_save=on_save, on_cancel=self.close_modal,
        )
        self.open_modal(mdl)