from PyQt5.QtWidgets import *
import app.database as db
from app.widgets.base_modal import BaseModal
from app.validators import validate_student_id, validate_student_name

class StudentModal(BaseModal):
    def __init__(self, parent=None, *, sid="", firstname="", lastname="",
                 course="", year=1, gender="Male", edit_mode=False,
                 on_save=None, on_cancel=None):
        super().__init__(parent)
        self.edit_mode = edit_mode
        self.on_save   = on_save
        self.on_cancel = on_cancel
        self.setFixedWidth(500)
        self.build_ui(sid, firstname, lastname, course, year, gender)
        self.val_timer.start(0)

    def build_ui(self, sid, firstname, lastname, course, year, gender):
        lay = QVBoxLayout(self)
        lay.setSpacing(14)
        lay.setContentsMargins(30, 28, 30, 28)

        lbl = QLabel("STUDENT ID  (YYYY-NNNN)"); lbl.setObjectName("mdl_lbl")
        lay.addWidget(lbl)
        self.inp_id = QLineEdit(sid)
        self.inp_id.setObjectName("mdl_input")
        self.inp_id.setPlaceholderText("e.g. 2024-0001")
        self.inp_id.setMaxLength(9)
        if self.edit_mode:
            self.inp_id.setReadOnly(True)
        lay.addWidget(self.inp_id)

        grid = QGridLayout(); grid.setSpacing(10)
        lf = QLabel("FIRST NAME"); lf.setObjectName("mdl_lbl")
        ll = QLabel("LAST NAME");  ll.setObjectName("mdl_lbl")
        self.inp_fn = QLineEdit(firstname); self.inp_fn.setObjectName("mdl_input")
        self.inp_ln = QLineEdit(lastname);  self.inp_ln.setObjectName("mdl_input")
        self.inp_fn.setPlaceholderText("First name")
        self.inp_ln.setPlaceholderText("Last name")
        grid.addWidget(lf, 0, 0); grid.addWidget(self.inp_fn, 1, 0)
        grid.addWidget(ll, 0, 1); grid.addWidget(self.inp_ln, 1, 1)
        lay.addLayout(grid)

        self.inp_id.textChanged.connect(self.on_input_changed)
        self.inp_fn.textChanged.connect(self.on_input_changed)
        self.inp_ln.textChanged.connect(self.on_input_changed)
        self.install_tooltip_filter(self.inp_id)
        self.install_tooltip_filter(self.inp_fn)
        self.install_tooltip_filter(self.inp_ln)

        grid2 = QGridLayout(); grid2.setSpacing(10)
        lc = QLabel("COLLEGE"); lc.setObjectName("mdl_lbl")
        lp = QLabel("COURSE");  lp.setObjectName("mdl_lbl")
        self.inp_college = QComboBox(); self.inp_college.setObjectName("mdl_combo")
        self.inp_course = QComboBox(); self.inp_course.setObjectName("mdl_combo")
        colleges = ["Unregistered"] + db.get_college_codes()
        self.inp_college.addItems(colleges)
        self.inp_college.currentTextChanged.connect(self.on_college_changed)
        grid2.addWidget(lc, 0, 0); grid2.addWidget(self.inp_college, 1, 0)
        grid2.addWidget(lp, 0, 1); grid2.addWidget(self.inp_course,  1, 1)
        lay.addLayout(grid2)
        self.init_college_course(course)

        grid3 = QGridLayout(); grid3.setSpacing(10)
        ly = QLabel("YEAR LEVEL"); ly.setObjectName("mdl_lbl")
        lg = QLabel("GENDER");     lg.setObjectName("mdl_lbl")
        self.inp_year = QSpinBox(); self.inp_year.setObjectName("mdl_spin")
        self.inp_year.setRange(1, 5); self.inp_year.setValue(year)
        self.inp_year.setSuffix("  ")
        self.inp_gender = QComboBox(); self.inp_gender.setObjectName("mdl_combo")
        self.inp_gender.addItems(["Male", "Female"])
        self.inp_gender.setCurrentText(gender)
        grid3.addWidget(ly, 0, 0); grid3.addWidget(self.inp_year,   1, 0)
        grid3.addWidget(lg, 0, 1); grid3.addWidget(self.inp_gender, 1, 1)
        lay.addLayout(grid3)

        lay.addSpacing(6)
        btns = QHBoxLayout(); btns.setSpacing(10); btns.addStretch()
        cancel = QPushButton("Cancel"); cancel.setObjectName("cancel_btn")
        self.save_btn = QPushButton("Save"); self.save_btn.setObjectName("save_btn")
        cancel.clicked.connect(self.handle_cancel)
        self.save_btn.clicked.connect(self.validate_and_save)
        btns.addWidget(cancel)
        btns.addWidget(self.save_btn)
        lay.addLayout(btns)

    def init_college_course(self, course):
        if not course:
            self.inp_college.setCurrentText("Unregistered")
            self.on_college_changed("Unregistered")
            return

        all_programs = db.get_programs_with_college()
        college_of_course = None
        for p in all_programs:
            if p["code"] == course:
                college_of_course = p["college"]
                break

        if college_of_course:
            self.inp_college.setCurrentText(college_of_course)
            self.on_college_changed(college_of_course)
        else:
            self.inp_college.setCurrentText("Unregistered")
            self.on_college_changed("Unregistered")

        idx = self.inp_course.findText(course)
        if idx >= 0:
            self.inp_course.setCurrentIndex(idx)

    def on_college_changed(self, college):
        self.inp_course.blockSignals(True)
        self.inp_course.clear()
        if college == "Unregistered":
            self.inp_course.addItem("None")
            self.inp_course.setEnabled(False)
        else:
            codes = db.get_program_codes_by_college(college) 
            self.inp_course.addItems(codes)
            self.inp_course.setEnabled(True)
        self.inp_course.blockSignals(False)

    def handle_cancel(self):
        if self.on_cancel:
            self.on_cancel()
        self.close()

    def validate_and_save(self):
        if not self.all_fields_filled():
            return
        if self.on_save:
            self.on_save(self.get_data())
        self.close()

    def all_fields_filled(self) -> bool:
        return bool(self.inp_id.text().strip() and
                    self.inp_fn.text().strip() and
                    self.inp_ln.text().strip())

    def update_save_btn(self):
        self.save_btn.setEnabled(self.all_fields_filled())

    def run_validation(self):
        if not self.user_touched:
            return
        ok = True

        state, tip = validate_student_id(self.inp_id.text(), self.edit_mode)
        if state is not None:
            self.set_field_state(self.inp_id, state, tip)
        if state != "valid":
            ok = False

        state, tip = validate_student_name(self.inp_fn.text())
        if state is not None:
            self.set_field_state(self.inp_fn, state, tip)
        if state != "valid":
            ok = False

        state, tip = validate_student_name(self.inp_ln.text())
        if state is not None:
            self.set_field_state(self.inp_ln, state, tip)
        if state != "valid":
            ok = False

        self.save_btn.setEnabled(ok)

    def get_data(self) -> tuple:
        course_val = self.inp_course.currentText()
        return (
            self.inp_id.text().strip(),
            self.inp_fn.text().strip(),
            self.inp_ln.text().strip(),
            None if course_val == "None" else course_val,
            self.inp_year.value(),
            self.inp_gender.currentText(),
        )
    