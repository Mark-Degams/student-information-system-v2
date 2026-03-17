from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QSpinBox, QPushButton, QMessageBox,
)
import app.database as db

class StudentModal(QWidget):
    def __init__(self, parent=None, *, sid="", firstname="", lastname="",
                 course="", year=1, gender="Male", edit_mode=False,
                 on_save=None, on_cancel=None):
        super().__init__(parent)
        self._edit_mode = edit_mode
        self._on_save   = on_save
        self._on_cancel = on_cancel
        self.setFixedWidth(500)
        self._build_ui(sid, firstname, lastname, course, year, gender)

    def _build_ui(self, sid, firstname, lastname, course, year, gender):
        lay = QVBoxLayout(self)
        lay.setSpacing(14)
        lay.setContentsMargins(30, 28, 30, 28)

        lbl = QLabel("STUDENT ID  (YYYY-NNNN)"); lbl.setObjectName("mdl_lbl")
        lay.addWidget(lbl)
        self.inp_id = QLineEdit(sid)
        self.inp_id.setObjectName("mdl_input")
        self.inp_id.setPlaceholderText("e.g. 2024-0001")
        self.inp_id.setMaxLength(9)
        if self._edit_mode:
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

        lbl = QLabel("COURSE"); lbl.setObjectName("mdl_lbl")
        lay.addWidget(lbl)
        self.inp_course = QComboBox(); self.inp_course.setObjectName("mdl_combo")
        codes = db.get_program_codes()
        self.inp_course.addItems(codes)
        if course in codes:
            self.inp_course.setCurrentText(course)
        lay.addWidget(self.inp_course)

        grid2 = QGridLayout(); grid2.setSpacing(10)
        ly = QLabel("YEAR LEVEL"); ly.setObjectName("mdl_lbl")
        lg = QLabel("GENDER");     lg.setObjectName("mdl_lbl")
        self.inp_year = QSpinBox(); self.inp_year.setObjectName("mdl_spin")
        self.inp_year.setRange(1, 4); self.inp_year.setValue(year)
        self.inp_year.setSuffix("  ")
        self.inp_gender = QComboBox(); self.inp_gender.setObjectName("mdl_combo")
        self.inp_gender.addItems(["Male", "Female"])
        self.inp_gender.setCurrentText(gender)
        grid2.addWidget(ly, 0, 0); grid2.addWidget(self.inp_year,   1, 0)
        grid2.addWidget(lg, 0, 1); grid2.addWidget(self.inp_gender, 1, 1)
        lay.addLayout(grid2)

        lay.addSpacing(6)
        btns = QHBoxLayout(); btns.setSpacing(10); btns.addStretch()
        cancel = QPushButton("Cancel"); cancel.setObjectName("cancel_btn")
        save   = QPushButton("Save");   save.setObjectName("save_btn")
        cancel.clicked.connect(self._handle_cancel)
        save.clicked.connect(self._validate_and_save)
        btns.addWidget(cancel)
        btns.addWidget(save)
        lay.addLayout(btns)

    def _handle_cancel(self):
        if self._on_cancel:
            self._on_cancel()

    def _validate_and_save(self):
        sid = self.inp_id.text().strip()
        if not db.validate_student_id(sid):
            QMessageBox.warning(self, "Validation", "ID must be in YYYY-NNNN format (e.g. 2024-0001).")
            self.inp_id.setFocus()
            return
        if not self.inp_fn.text().strip():
            QMessageBox.wa