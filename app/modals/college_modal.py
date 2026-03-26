from PyQt5.QtWidgets import *
from PyQt5.QtGui import QColor
import app.database as db
from app.modals.base_modal import BaseModal
from app.widgets.badge import load_badge_colors, save_badge_color
from app.validators import validate_college_code, validate_college_name

class CollegeModal(BaseModal):
    def __init__(self, parent=None, *, code="", name="",
                 bg_color="#e2e8f0", fg_color="#4a5568",
                 edit_mode=False, on_save=None, on_cancel=None):
        super().__init__(parent)
        self.edit_mode = edit_mode
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.orig_code = code

        existing = load_badge_colors().get(code, (bg_color, fg_color))
        self.bg_color = existing[0]
        self.fg_color = existing[1]

        self.setFixedWidth(500)
        self.build_ui(code, name)
        self.val_timer.start(0)

    def build_ui(self, code, name):
        lay = QVBoxLayout(self)
        lay.setSpacing(14)
        lay.setContentsMargins(30, 28, 30, 28)

        lbl = QLabel("COLLEGE CODE"); lbl.setObjectName("mdl_lbl")
        lay.addWidget(lbl)
        self.inp_code = QLineEdit(code)
        self.inp_code.setObjectName("mdl_input")
        self.inp_code.setPlaceholderText("e.g. CCS")
        self.inp_code.setMaxLength(8)
        lay.addWidget(self.inp_code)

        lbl = QLabel("COLLEGE NAME"); lbl.setObjectName("mdl_lbl")
        lay.addWidget(lbl)
        self.inp_name = QLineEdit(name)
        self.inp_name.setObjectName("mdl_input")
        self.inp_name.setPlaceholderText("e.g. College of Computer Studies")
        lay.addWidget(self.inp_name)

        lbl = QLabel("BADGE COLOR"); lbl.setObjectName("mdl_lbl")
        lay.addWidget(lbl)
        frame = QFrame(); frame.setObjectName("section_box")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(12, 10, 12, 10)
        frame_layout.setSpacing(8)
        color_row = QHBoxLayout()
        color_row.setSpacing(8)

        bg_label = QLabel("Background"); bg_label.setObjectName("mdl_lbl")
        self.bg_btn = QPushButton(); self.bg_btn.setObjectName("color_btn")
        self.bg_btn.setFixedSize(32, 32)
        self.bg_btn.setStyleSheet(f"QPushButton#color_btn {{ background: {self.bg_color}; }}")
        self.bg_btn.clicked.connect(self.pick_bg)

        fg_label = QLabel("Text"); fg_label.setObjectName("mdl_lbl")
        self.fg_btn = QPushButton(); self.fg_btn.setObjectName("color_btn")
        self.fg_btn.setFixedSize(32, 32)
        self.fg_btn.setStyleSheet(f"QPushButton#color_btn {{ background: {self.fg_color}; }}")
        self.fg_btn.clicked.connect(self.pick_fg)

        color_row.addWidget(bg_label)
        color_row.addWidget(self.bg_btn)
        color_row.addSpacing(12)
        color_row.addWidget(fg_label)
        color_row.addWidget(self.fg_btn)
        color_row.addStretch()
        frame_layout.addLayout(color_row)
        
        lay.addWidget(frame)

        self.install_tooltip_filter(self.inp_code)
        self.install_tooltip_filter(self.inp_name)

        lay.addSpacing(6)
        btns = QHBoxLayout(); btns.setSpacing(10); btns.addStretch()
        cancel = QPushButton("Cancel"); cancel.setObjectName("cancel_btn")
        self.save_btn = QPushButton("Save"); self.save_btn.setObjectName("save_btn")
        cancel.clicked.connect(self.handle_cancel)
        self.save_btn.clicked.connect(self.validate_and_save)
        btns.addWidget(cancel)
        btns.addWidget(self.save_btn)
        self.inp_code.textChanged.connect(self.on_input_changed)
        self.inp_name.textChanged.connect(self.on_input_changed)
        lay.addLayout(btns)

    def make_section(self, layout):
        frame = QFrame()
        frame.setObjectName("section_box")
        frame.setLayout(layout)
        return frame

    def pick_bg(self):
        c = QColorDialog.getColor(QColor(self.bg_color), self, "Badge Background")
        if c.isValid():
            self.bg_color = c.name()
            self.bg_btn.setStyleSheet(f"background:{self.bg_color}; border-radius:6px; border:1px solid #e2e8f0;")

    def pick_fg(self):
        c = QColorDialog.getColor(QColor(self.fg_color), self, "Badge Text Color")
        if c.isValid():
            self.fg_color = c.name()
            self.fg_btn.setStyleSheet(f"background:{self.fg_color}; border-radius:6px; border:1px solid #e2e8f0;")
        
    def handle_cancel(self):
        if self.on_cancel:
            self.on_cancel()
        self.close()

    def validate_and_save(self):
        if not self.all_fields_filled():
            return
        code = self.inp_code.text().strip().upper()
        if self.on_save:
            save_badge_color(code, self.bg_color, self.fg_color)
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

        state, tip = validate_college_code(self.inp_code.text(), self.edit_mode, self.orig_code)
        if state is not None:
            self.set_field_state(self.inp_code, state, tip)
        if state != "valid":
            ok = False

        state, tip = validate_college_name(self.inp_name.text())
        if state is not None:
            self.set_field_state(self.inp_name, state, tip)
        if state != "valid":
            ok = False

        self.save_btn.setEnabled(ok)

    def get_data(self) -> tuple:
        return (
            self.inp_code.text().strip(),
            self.inp_name.text().strip(),

        )