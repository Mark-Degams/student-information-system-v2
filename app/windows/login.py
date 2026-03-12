from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
)
from PyQt5.QtCore import Qt, pyqtSignal
import app.database as db


class LoginView(QWidget):
    # Emitted on successful login: (role, display_name)
    login_success = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("login_bg")
        self._role = "admin"      # currently selected tab
        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignCenter)
        outer.setContentsMargins(0, 0, 0, 0)

        # ── Card ──────────────────────────────────────────────────
        card = QFrame()
        card.setObjectName("login_card")
        card.setFixedWidth(420)
        card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        outer.addWidget(card, alignment=Qt.AlignCenter)

        lay = QVBoxLayout(card)
        lay.setSpacing(14)
        lay.setContentsMargins(38, 38, 38, 38)

        # Title
        title = QLabel("SSIS"); title.setObjectName("login_title")
        sub   = QLabel("Student Information System"); sub.setObjectName("login_sub")
        lay.addWidget(title)
        lay.addWidget(sub)
        lay.addSpacing(6)

        # ── Role tabs ──────────────────────────────────────────────
        role_bar = QWidget(); role_bar.setObjectName("role_bar")
        rb_lay   = QHBoxLayout(role_bar)
        rb_lay.setContentsMargins(4, 4, 4, 4); rb_lay.setSpacing(4)

        self._tab_admin   = QPushButton("👤  Admin");   self._tab_admin.setObjectName("role_tab")
        self._tab_student = QPushButton("🎓  Student"); self._tab_student.setObjectName("role_tab")
        self._tab_admin.setFixedHeight(36)
        self._tab_student.setFixedHeight(36)
        self._tab_admin.clicked.connect(lambda: self._switch_role("admin"))
        self._tab_student.clicked.connect(lambda: self._switch_role("student"))
        rb_lay.addWidget(self._tab_admin)
        rb_lay.addWidget(self._tab_student)
        lay.addWidget(role_bar)

        # ── Username / ID ──────────────────────────────────────────
        self._lbl_user = QLabel("USERNAME"); self._lbl_user.setObjectName("dlg_lbl")
        lay.addWidget(self._lbl_user)
        self._inp_user = QLineEdit(); self._inp_user.setObjectName("login_input")
        self._inp_user.setPlaceholderText("Enter username")
        self._inp_user.returnPressed.connect(self._do_login)
        lay.addWidget(self._inp_user)

        # ── Password / ID Number ───────────────────────────────────
        self._lbl_pass = QLabel("PASSWORD"); self._lbl_pass.setObjectName("dlg_lbl")
        lay.addWidget(self._lbl_pass)
        self._inp_pass = QLineEdit(); self._inp_pass.setObjectName("login_input")
        self._inp_pass.setEchoMode(QLineEdit.Password)
        self._inp_pass.setPlaceholderText("Enter password")
        self._inp_pass.returnPressed.connect(self._do_login)
        lay.addWidget(self._inp_pass)

        # ── Error label (hidden until error) ──────────────────────
        self._lbl_error = QLabel()
        self._lbl_error.setObjectName("login_error")
        self._lbl_error.setWordWrap(True)
        self._lbl_error.hide()
        lay.addWidget(self._lbl_error)

        # ── Sign In button ─────────────────────────────────────────
        self._btn_login = QPushButton("Sign In"); self._btn_login.setObjectName("login_btn")
        self._btn_login.setFixedHeight(46)
        self._btn_login.clicked.connect(self._do_login)
        lay.addWidget(self._btn_login)

        # ── Hint ───────────────────────────────────────────────────
        self._lbl_hint = QLabel(
            "Admin →  username: <b>admin</b>  /  password: <b>admin1234</b>"
        )
        self._lbl_hint.setObjectName("login_hint")
        self._lbl_hint.setTextFormat(Qt.RichText)
        self._lbl_hint.setWordWrap(True)
        lay.addWidget(self._lbl_hint)

        self._switch_role("admin")

    # ── logic ─────────────────────────────────────────────────────────────────

    def _switch_role(self, role: str):
        self._role = role
        is_admin = (role == "admin")

        for btn, active in [(self._tab_admin, is_admin), (self._tab_student, not is_admin)]:
            btn.setProperty("active", "true" if active else "false")
            btn.style().unpolish(btn); btn.style().polish(btn)

        if is_admin:
            self._lbl_user.setText("USERNAME")
            self._inp_user.setPlaceholderText("Enter username")
            self._lbl_pass.setText("PASSWORD")
            self._inp_pass.setPlaceholderText("Enter password")
            self._inp_pass.setEchoMode(QLineEdit.Password)
            self._lbl_hint.setText(
                "Admin →  username: <b>admin</b>  /  password: <b>admin1234</b>"
            )
            self._lbl_hint.show()
        else:
            self._lbl_user.setText("FULL NAME")
            self._inp_user.setPlaceholderText("Enter your full name")
            self._lbl_pass.setText("STUDENT ID  (YYYY-NNNN)")
            self._inp_pass.setPlaceholderText("e.g. 2021-0001")
            self._inp_pass.setEchoMode(QLineEdit.Normal)
            self._lbl_hint.setText(
                "Student →  enter your full name and ID number"
            )
            self._lbl_hint.show()

        self._lbl_error.hide()
        self._inp_user.clear()
        self._inp_pass.clear()
        self._inp_user.setFocus()

    def _do_login(self):
        username = self._inp_user.text().strip()
        password = self._inp_pass.text().strip()

        if self._role == "admin":
            if username == "admin" and password == "admin1234":
                self.login_success.emit("admin", "Administrator")
            else:
                self._show_error("Invalid admin credentials.")

        elif self._role == "student":
            with db.get_db() as conn:
                row = conn.execute(
                    "SELECT * FROM student WHERE LOWER(firstname||' '||lastname)=LOWER(?) AND id=?",
                    (username, password),
                ).fetchone()
            if row:
                name = f"{row['firstname']} {row['lastname']}"
                self.login_success.emit("student", name)
            else:
                self._show_error("Student not found. Check your full name and ID number.")

    def _show_error(self, msg: str):
        self._lbl_error.setText(msg)
        self._lbl_error.show()

    def clear(self):
        self._inp_user.clear()
        self._inp_pass.clear()
        self._lbl_error.hide()
        self._switch_role("admin")
