from PyQt5.QtWidgets import *
import app.database as db

class ProgramModal(QWidget):
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
        save   = QPushButton("Save");   save.setObjectName("save_btn")
        cancel.clicked.connect(self.handle_cancel)
        save.clicked.connect(self.validate_and_save)
        btns.addWidget(cancel)
        btns.addWidget(save)
        lay.addLayout(btns)

    def handle_cancel(self):
        if self.on_cancel:
            self.on_cancel()
        self.close()

    def validate_and_save(self):
        code = self.inp_code.text().strip().upper()
        if db.code_exists(code):
            if self.edit_mode:
                if code != self.orig_code:
                    QMessageBox.warning(self, "Validation", "Program code already exists.")
                    return
            else:
                QMessageBox.warning(self, "Validation", "Program code already exists.")
                return
        if not self.inp_code.text().strip():
            QMessageBox.warning(self, "Validation", "Program code is required.")
            return
        if not self.inp_name.text().strip():
            QMessageBox.warning(self, "Validation", "Program name is required.")
            return
        if not self.inp_col.currentText():
            QMessageBox.warning(self, "Validation", "College is required.")
            return
        if self.on_save:
            self.on_save(*self.get_data())
        self.close()

    def get_data(self) -> tuple:
        return (
            self.inp_code.text().strip(),
            self.inp_name.text().strip(),
            self.inp_col.currentText(),
        )