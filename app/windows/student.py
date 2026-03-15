
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from app.widgets.table import TablePage
import app.database as db


class StudentWin(TablePage):
    HEADERS   = ["ID Number", "First Name", "Last Name", "Course", "Year", "Gender", "Actions"]
    SORT_KEYS = ["id", "firstname", "lastname", "course", "year", "gender", "id"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.load()

    def set_column_widths(self):
        self.table.setColumnWidth(0, 120)
        self.table.setColumnWidth(1, 140)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 110)
        self.table.setColumnWidth(4, 65)
        self.table.setColumnWidth(5, 85)

    def fetch(self, q, sort_key, asc, limit, offset):
        return db.student_list(q, sort_key, asc, limit, offset)

    def populate_row(self, row_idx, rec):
        self.set_text(row_idx, 0, rec["id"])
        self.set_text(row_idx, 1, rec["firstname"])
        self.set_text(row_idx, 2, rec["lastname"])
        self.set_text(row_idx, 3, rec["course"])
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
        pass

    def add_new(self):
        pass