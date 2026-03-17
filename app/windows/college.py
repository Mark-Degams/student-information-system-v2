from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from app.widgets.table import TablePage
import app.database as db

class CollegeWin(TablePage):
    HEADERS   = ["Code", "Name", "Programs", "Actions"]
    SORT_KEYS = ["code", "name", "programs", "code"]
    FIXED_WIDTHS = {0: 130, 2: 100, 3: 150}
    FLEX_RATIOS = {1: 1} 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.overlay = None
        self.load()

    def fetch(self, q, sort_key, asc, limit, offset):
        return db.college_list(q, sort_key, asc, limit, offset)

    def populate_row(self, row_idx, rec):
        self.set_badge(row_idx, 0, rec["code"], rec["code"])
        self.set_text(row_idx, 1, rec["name"])
        self.set_text(row_idx, 2, str(rec["programs"]), Qt.AlignCenter | Qt.AlignVCenter)
        self.set_actions(
            row_idx,
            on_edit=lambda _, r=rec: self.edit(r),
            on_delete=lambda _, r=rec: self.delete(r),
        )

    def add_new(self):
        pass

    def edit(self, rec):
        pass

    def delete(self, rec):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete college '{rec['code']} - {rec['name']}'?\n"
            f"This will fail if programs are still linked to it.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        try:
            db.college_delete(rec["code"])
            self.load()
        except ValueError as e:
            QMessageBox.warning(self, "Cannot Delete", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
