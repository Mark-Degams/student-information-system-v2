from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from app.widgets.table import TablePage
from app.widgets.modal_overlay import ModalOverlay
from app.modals.program_modal import ProgramModal
import app.database as db

class ProgramWin(TablePage):
    HEADERS   = ["Code", "Name", "College", "Students", "Actions"]
    SORT_KEYS = ["code", "name", "college_name", "students", "actions"]
    FIXED_WIDTHS = {0: 150, 2: 150, 3: 100, 4: 150}
    FLEX_RATIOS = {1: 1} 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.overlay = None
        self.load()

    def open_modal(self, modal_widget: ProgramModal):
        self.close_modal()            
        self.overlay = ModalOverlay(self, modal_widget)
        self.overlay.setGeometry(0, 0, self.width(), self.height())

    def close_modal(self):
        if self.overlay:
            self.overlay.close_overlay()
            self.overlay = None

    def fetch(self, q, sort_key, asc, limit, offset):
        return db.program_list(q, sort_key, asc, limit, offset)

    def populate_row(self, row_idx, rec):
        self.set_text(row_idx, 0, rec["code"])
        self.set_text(row_idx, 1, rec["name"])
        self.set_badge(row_idx, 2, f"{rec['college']}", rec["college"])
        self.set_text(row_idx, 3, str(rec["students"]), Qt.AlignCenter | Qt.AlignVCenter)
        self.set_actions(
            row_idx,
            on_edit=lambda _, r=rec: self.edit(r),
            on_delete=lambda _, r=rec: self.delete(r),
        )

    def add_new(self):
        def on_save(code, name, college):
            try:
                db.program_add(code, name, college)
                self.close_modal()
                self.load()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

        mdl = ProgramModal(self, on_save=on_save, on_cancel=self.close_modal)
        self.open_modal(mdl)

    def edit(self, rec):
        def on_save(code, name, college):
            try:
                db.program_update(rec["code"], code, name, college)
                self.close_modal()
                self.load()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

        mdl = ProgramModal(
            self, code=rec["code"], name=rec["name"],
            college=rec["college"], edit_mode=True, on_save=on_save, 
            on_cancel=self.close_modal,
        )
        self.open_modal(mdl)

    def delete(self, rec):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete program '{rec['code']} - {rec['name']}'?\n"
            f"This will fail if students are still enrolled.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        try:
            db.program_delete(rec["code"])
            self.load()
        except ValueError as e:
            QMessageBox.warning(self, "Cannot Delete", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
