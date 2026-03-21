from PyQt5.QtWidgets import QMessageBox, QMenu, QAction
from PyQt5.QtCore import Qt
from app.widgets.table import TablePage
from app.widgets.modal_overlay import ModalOverlay
from app.widgets.group_modal import GroupEditModal
from app.modals.student_modal import StudentModal
from app.modals.delete_modal import DeleteModal
import app.database as db


class StudentWin(TablePage):
    HEADERS = ["ID Number", "First Name", "Last Name", "Course", "Year", "Gender", "Actions"]
    SORT_KEYS = ["id", "firstname", "lastname", "course", "year", "gender", "actions"]
    FIXED_WIDTHS = {0: 110, 3: 150, 4: 70, 5: 85, 6: 150}
    FLEX_RATIOS = {1: 0.55, 2: 0.45} 

    def __init__(self, parent=None, show_notify=None):
        super().__init__(parent)
        self.overlay = None
        self.show_notify = show_notify
        self.load()

    def open_modal(self, modal_widget: StudentModal):
        self.close_modal()            
        self.overlay = ModalOverlay(self, modal_widget)
        self.overlay.setGeometry(0, 0, self.width(), self.height())

    def close_modal(self):
        if self.overlay:
            self.overlay.close_overlay()
            self.overlay = None

    def fetch(self, q, sort_key, asc, limit, offset, field="All Fields"):
        return db.student_list(q, sort_key, asc, limit, offset, field)

    def populate_row(self, row_idx, rec):
        self.set_text(row_idx, 0, rec["id"])
        self.set_text(row_idx, 1, rec["firstname"])
        self.set_text(row_idx, 2, rec["lastname"])
        self.set_badge(row_idx, 3, rec["course"] or "N/A", rec.get("college_code"))
        self.set_text(row_idx, 4, str(rec["year"]), Qt.AlignCenter | Qt.AlignVCenter)
        self.set_text(row_idx, 5, rec["gender"])
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
        course_action = QAction(f"Change Course ({len(selected)} students)", self)
        year_action = QAction(f"Change Year ({len(selected)} students)", self)
        delete_action = QAction(f"Delete ({len(selected)} students)", self)
        course_action.triggered.connect(lambda: self.group_edit_course(selected))
        year_action.triggered.connect(lambda: self.group_edit_year(selected))
        delete_action.triggered.connect(lambda: self.group_delete(selected))
        menu.addAction(course_action)
        menu.addAction(year_action)
        menu.addSeparator()
        menu.addAction(delete_action)
        menu.exec_(self.table.viewport().mapToGlobal(pos))

    def group_edit_course(self, selected):
        rows = [[r["id"], r["firstname"], r["lastname"], r["course"] or "N/A"] for r in selected]

        def on_confirm(values):
            try:
                new_course = None if values["course"] == "None" else values["course"]
                for rec in selected:
                    db.student_update(
                        rec["id"], rec["firstname"], rec["lastname"],
                        new_course, rec["year"], rec["gender"]
                    )
                self.close_modal()
                self.load()
                if self.show_notify:
                    self.show_notify(f"<b>{len(selected)}</b> students' course updated.", "edit")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

        colleges = ["Unregistered"] + db.get_college_codes()

        mdl = GroupEditModal(
            self,
            title="Change Course",
            record_headers=["ID", "First Name", "Last Name", "Course"],
            record_rows=rows,
            fields=[
                {"key": "college", "label": "COLLEGE", "type": "combo",
                "items": colleges, "current": ""},
                {"key": "course", "label": "NEW COURSE", "type": "combo",
                "items": ["None"], "current": ""},
            ],
            on_confirm=on_confirm,
            on_cancel=self.close_modal,
            cascade={"parent_key": "college", "child_key": "course",
                    "resolver": lambda col: ["None"] if col == "Unregistered"
                                else db.get_program_codes_by_college(col)},
        )
        self.open_modal(mdl)

    def group_edit_year(self, selected):
        rows = [[r["id"], r["firstname"], r["lastname"], str(r["year"])] for r in selected]

        def on_confirm(values):
            try:
                new_year = values["year"]
                for rec in selected:
                    db.student_update(
                        rec["id"], rec["firstname"], rec["lastname"],
                        rec["course"], new_year, rec["gender"]
                    )
                self.close_modal()
                self.load()
                self.show_notify(f"<b>{len(selected)}</b> students' year updated.", "edit")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

        mdl = GroupEditModal(
            self,
            title="Change Year Level",
            record_headers=["ID", "First Name", "Last Name", "Year"],
            record_rows=rows,
            fields=[
                {"key": "year", "label": "NEW YEAR LEVEL", "type": "spin",
                "min": 1, "max": 5, "value": 1},
            ],
            on_confirm=on_confirm,
            on_cancel=self.close_modal,
        )
        self.open_modal(mdl)

    def group_delete(self, selected):
        rows = [[r["id"], r["firstname"], r["lastname"]] for r in selected]

        from app.modals.delete_modal import DeleteModal
        def on_confirm():
            try:
                for rec in selected:
                    db.student_delete(rec["id"])
                self.close_modal()
                self.load()
                if self.show_notify:
                    self.show_notify(f"<b>{len(selected)}</b> students deleted.", "delete")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

        mdl = DeleteModal(
            self,
            title=f"Delete {len(selected)} Students?",
            message="You are about to delete the following students. This cannot be undone.",
            affected_label=f"Selected Students ({len(selected)})",
            headers=["ID", "First Name", "Last Name"],
            rows=rows,
            visible_rows=5,
            on_confirm=on_confirm,
            on_cancel=self.close_modal,
            danger_label=f"Delete {len(selected)} Students",
        )
        self.open_modal(mdl)
        
    def add_new(self):
        if self.readonly:
            return
        def on_save(data):
            try:
                db.student_add(*data)
                self.close_modal()
                self.load()
                self.show_notify(f"Student '<b>{data[0]}</b>' added successfully.", "success")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

        mdl = StudentModal(
            on_save=on_save, on_cancel=self.close_modal,
        )
        self.open_modal(mdl)

    def edit(self, rec):
        def on_save(data):
            try:
                db.student_update(*data)
                self.close_modal()
                self.load()
                self.show_notify(f"Student '<b>{rec['id']}</b>' edited successfully.", "edit")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

        mdl = StudentModal(
            sid=rec["id"], firstname=rec["firstname"], lastname=rec["lastname"],
            course=rec["course"], year=rec["year"], gender=rec["gender"],
            edit_mode=True, on_save=on_save, on_cancel=self.close_modal,
        )
        self.open_modal(mdl)

    def delete(self, rec):
        def on_confirm():
            try:
                db.student_delete(rec["id"])
                self.close_modal()
                self.load()
                self.show_notify(f"Student '<b>{rec['id']}</b>' deleted successfully.", "delete")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

        mdl = DeleteModal(
            self,
            title=f"Delete '{rec['id']}'?",
            message=f"You are about to delete student \"{rec['firstname']} {rec['lastname']}\". This cannot be undone.",
            on_confirm=on_confirm,
            on_cancel=self.close_modal,
            danger_label="Delete Student",
        )
        self.open_modal(mdl)