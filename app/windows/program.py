from PyQt5.QtWidgets import QMessageBox, QMenu, QAction
from PyQt5.QtCore import Qt
from app.widgets.table import TablePage
from app.widgets.modal_overlay import ModalOverlay
from app.modals.group_modal import GroupEditModal
from app.modals.program_modal import ProgramModal
from app.modals.delete_modal import DeleteModal
from app.modals.profile_modal import ProgramProfile, ProfileOverlay
import app.database as db

class ProgramWin(TablePage):
    HEADERS   = ["Code", "Name", "College", "Students", "Actions"]
    SORT_KEYS = ["code", "name", "college_name", "students", "actions"]
    FIXED_WIDTHS = {0: 150, 2: 150, 3: 100, 4: 150}
    FLEX_RATIOS = {1: 1} 

    def __init__(self, parent=None, show_notify=None):
        super().__init__(parent)
        self.overlay = None
        self.show_notify = show_notify
        self.table.cellDoubleClicked.connect(self.on_double_click)
        self.load()

    def open_modal(self, modal_widget: ProgramModal):
        self.close_modal()            
        self.overlay = ModalOverlay(self, modal_widget)
        self.overlay.setGeometry(0, 0, self.width(), self.height())

    def close_modal(self):
        if self.overlay:
            self.overlay.close_overlay()
            self.overlay = None

    def fetch(self, q, sort_key, asc, limit, offset, field="All Fields"):
        return db.program_list(q, sort_key, asc, limit, offset)

    def populate_row(self, row_idx, rec):
        self.set_text(row_idx, 0, rec["code"])
        self.set_text(row_idx, 1, rec["name"])
        self.set_badge(row_idx, 2, rec["college"] or "N/A", rec["college"] or "")
        self.set_text(row_idx, 3, str(rec["students"]), Qt.AlignCenter | Qt.AlignVCenter)
        self.set_actions(
            row_idx,
            on_edit=lambda _, r=rec: self.edit(r),
            on_delete=lambda _, r=rec: self.delete(r),
        )

    def on_context_menu(self, pos):
        if self.readonly:
            return
        selected = self.get_selected_records()
        if len(selected) < 2:
            return

        menu = QMenu(self); menu.setObjectName("group_select_menu")
        edit_action = QAction(f"Group Edit ({len(selected)} programs)", self)
        edit_action.triggered.connect(lambda: self.group_edit(selected))
        menu.addAction(edit_action)
        menu.exec_(self.table.viewport().mapToGlobal(pos))

    def on_double_click(self, row, col):
        code_item = self.table.item(row, 0)
        if not code_item:
            return
        rows, _ = db.program_list(code_item.text(), "code", True, 1, 0)
        if rows:
            ProfileOverlay(self, ProgramProfile(rows[0]))

    def group_edit(self, selected):
        rows = [[r["code"], r["name"], r["college"] or "N/A"] for r in selected]
        colleges = db.get_college_codes()

        def on_confirm(values):
            try:
                new_college = values["college"]
                for rec in selected:
                    db.program_update(rec["code"], rec["code"], rec["name"], new_college)
                self.close_modal()
                self.load()
                self.show_notify(f"<b>{len(selected)}</b> programs updated successfully.", "edit")
            except Exception as e:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Error", str(e))

        mdl = GroupEditModal(
            self,
            title="Group Edit Programs",
            record_headers=["Code", "Name", "College"],
            record_rows=rows,
            fields=[
                {"key": "college", "label": "NEW COLLEGE", "type": "combo",
                "items": colleges, "current": ""},
            ],
            on_confirm=on_confirm,
            on_cancel=self.close_modal,
        )
        self.open_modal(mdl)

    def add_new(self):
        if self.readonly:
            return
        def on_save(code, name, college):
            try:
                db.program_add(code, name, college)
                self.close_modal()
                self.load()
                self.show_notify(f"Program '<b>{code}</b>' added successfully.", "success")
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
                self.show_notify(f"Program '<b>{code}</b>' edited successfully.", "edit")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

        mdl = ProgramModal(
            self, code=rec["code"], name=rec["name"],
            college=rec["college"], edit_mode=True, on_save=on_save, 
            on_cancel=self.close_modal,
        )
        self.open_modal(mdl)

    def delete(self, rec):
        affected = db.students_by_program(rec["code"]) 
        rows = [[s["id"], s["firstname"], s["lastname"]] for s in affected]

        def on_confirm():
            try:
                db.program_delete(rec["code"])
                self.close_modal()
                self.load()
                self.show_notify(f"Program '<b>{rec['code']}</b>' deleted successfully.", "delete")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

        mdl = DeleteModal(
            self,
            title=f"Delete '{rec['code']}'?",
            message=(
                f"You are about to delete the program \"{rec['name']}\".\n"
                f"All enrolled students will have their course set to None."
            ),
            affected_label=f"Affected Students ({len(affected)})",
            headers=["ID", "First Name", "Last Name"],
            rows=rows,
            visible_rows=5,
            on_confirm=on_confirm,
            on_cancel=self.close_modal,
            danger_label="Delete Program",
        )
        self.open_modal(mdl)