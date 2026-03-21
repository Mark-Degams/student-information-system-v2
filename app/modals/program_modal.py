from PyQt5.QtWidgets import *
import app.database as db
from app.widgets.base_modal import BaseModal
from app.validators import validate_program_code, validate_program_name

class ProgramModal(BaseModal):
    def __init__(self, parent=None, *, code="", name="",
                 college="", edit_mode=False, 
                 on_save=None, on_cancel=None):
        super().__init__(parent)
        self.edit_mode = edit_mode
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.orig_code = code
        self.setFixedWidth(500)
        self.build_ui(code, name, college)
        self.update_save_btn()

    def build_ui(self, code, name, college):
        lay = QVBoxLayout(self)
        lay.setSpacing(14)
        lay.setContentsMargins(30, 28, 30, 28)

        lbl = QLabel("PROGRAM CODE"); lbl.setObjectName("mdl_lbl")
        lay.addWidget(lbl)
        self.inp_code = QLineEdit(code)
        self.inp_code.setObjectName("mdl_input")
        self.inp_code.setPlaceholderText("e.g. BSCS")
        self.inp_code.setMaxLength(10)
        lay.addWidget(self.inp_code)

        lbl = QLabel("PROGRAM NAME"); lbl.setObjectName("mdl_lbl")
        lay.addWidget(lbl)
        self.inp_name = QLineEdit(name)
        self.inp_name.setObjectName("mdl_input")
        self.inp_name.setPlaceholderText("e.g. Bachelor of Science in Computer Science")
        lay.addWidget(self.inp_name)

        self.inp_code.textChanged.connect(self.on_input_changed)
        self.inp_name.textChanged.connect(self.on_input_changed)
        self.install_tooltip_filter(self.inp_code)
        self.install_tooltip_filter(self.inp_name)

        lbl = QLabel("COLLEGE"); lbl.setObjectName("mdl_lbl")
        lay.addWidget(lbl)
        self.inp_col = QComboBox(); self.inp_col.setObjectName("mdl_combo")
        colleges = db.get_college_codes()
        self.inp_col.addItems(colleges)
        if college in colleges:
            self.inp_col.setCurrentText(college)
        lay.addWidget(self.inp_col)

        lay.addSpacing(6)
        btns = QHBoxLayout(); btns.setSpacing(10); btns.addStretch()
        cancel = QPushButton("Cancel"); cancel.setObjectName("cancel_btn")
        self.save_btn = QPushButton("Save"); self.save_btn.setObjectName("save_btn")
        cancel.clicked.connect(self.handle_cancel)
        self.save_btn.clicked.connect(self.validate_and_save)
        btns.addWidget(cancel)
        btns.addWidget(self.save_btn)
        lay.addLayout(btns)

    def handle_cancel(self):
        if self.on_cancel:
            self.on_cancel()
        self.close()

    def validate_and_save(self):
        if not self.all_fields_filled():
            return
        if self.on_save:
            self.on_save(*self.get_data())
        self.close()

    def all_fields_filled(self) -> bool:
        return bool(self.inp_code.text().strip() and self.inp_name.text().strip())

    def update_save_btn(self):
        self.save_btn.setEnabled(self.all_fields_filled())

    def run_validation(self):
        if not self.user_touched:
            return
        ok = True

        state, tip = validate_program_code(self.inp_code.text(), self.edit_mode, self.orig_code)
        if state is not None:
            self.set_field_state(self.inp_code, state, tip)
        if state != "valid":
            ok = False

        state, tip = validate_program_name(self.inp_name.text())
        if state is not None:
            self.set_field_state(self.inp_name, state, tip)
        if state != "valid":
            ok = False

        self.save_btn.setEnabled(ok)

    def get_data(self) -> tuple:
        return (
            self.inp_code.text().strip(),
            self.inp_name.text().strip(),
            self.inp_col.currentText(),
        )