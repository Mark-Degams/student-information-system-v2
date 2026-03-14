from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
import app.database as db
from pathlib import Path

class LoginView(QWidget):
    login_success = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("login_bg")
        self.role = "admin"   
        self.build_ui()

    def build_ui(self):
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignCenter)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName("login_card")
        card.setFixedWidth(420)
        card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        outer.addWidget(card, alignment=Qt.AlignCenter)

        lay = QVBoxLayout(card)
        lay.setSpacing(14)
        lay.setContentsMargins(38, 38, 38, 38)

        title = QLabel("SSIS"); title.setObjectName("login_title")
        sub   = QLabel("Student Information System"); sub.setObjectName("login_sub")
        lay.addWidget(title)
        lay.addWidget(sub)
        lay.addSpacing(6)

        role_bar = QWidget(); role_bar.setObjectName("role_bar")
        rb_lay   = QHBoxLayout(role_bar)
        rb_lay.setContentsMargins(4, 4, 4, 4); rb_lay.setSpacing(4)

        admin_icon = QIcon(QPixmap(str(Path(__file__).resolve().parent.parent / "icons" / "person.svg")))
        self.tab_admin = QPushButton(admin_icon, " Admin")
        self.tab_admin.setObjectName("role_tab")
        self.tab_admin.setFixedHeight(36)
        self.tab_admin.clicked.connect(lambda: self.switchrole("admin"))

        student_icon = QIcon(QPixmap(str(Path(__file__).resolve().parent.parent / "icons" / "student.svg")))
        self.tab_student = QPushButton(student_icon, " Student")
        self.tab_student.setObjectName("role_tab")
        self.tab_student.setFixedHeight(36)
        self.tab_student.clicked.connect(lambda: self.switchrole("student"))

        rb_lay.addWidget(self.tab_admin)
        rb_lay.addWidget(self.tab_student)
        lay.addWidget(role_bar)

        self.lbl_user = QLabel("USERNAME"); self.lbl_user.setObjectName("dlg_lbl")
        lay.addWidget(self.lbl_user)
        self.inp_user = QLineEdit(); self.inp_user.setObjectName("login_input")
        self.inp_user.setPlaceholderText("Enter username")
        self.inp_user.returnPressed.connect(self.do_login)
        lay.addWidget(self.inp_user)

        self.lbl_pass = QLabel("PASSWORD"); self.lbl_pass.setObjectName("dlg_lbl")
        lay.addWidget(self.lbl_pass)
        self.inp_pass = QLineEdit(); self.inp_pass.setObjectName("login_input")
        self.inp_pass.setEchoMode(QLineEdit.Password)
        self.inp_pass.setPlaceholderText("Enter password")
        self.inp_pass.returnPressed.connect(self.do_login)
        lay.addWidget(self.inp_pass)

        self.lbl_error = QLabel()
        self.lbl_error.setObjectName("login_error")
        self.lbl_error.setWordWrap(True)
        self.lbl_error.hide()
        lay.addWidget(self.lbl_error)

        self.btn_login = QPushButton("Sign In"); self.btn_login.setObjectName("login_btn")
        self.btn_login.setFixedHeight(46)
        self.btn_login.clicked.connect(self.do_login)
        lay.addWidget(self.btn_login)

        self.lbl_hint = QLabel(
            "Admin →  username: <b>admin</b>  /  password: <b>admin1234</b>"
        )
        self.lbl_hint.setObjectName("login_hint")
        self.lbl_hint.setTextFormat(Qt.RichText)
        self.lbl_hint.setWordWrap(True)
        lay.addWidget(self.lbl_hint)

        self.switchrole("admin")

    def switchrole(self, role: str):
        self.role = role
        is_admin = (role == "admin")

        for btn, active in [(self.tab_admin, is_admin), (self.tab_student, not is_admin)]:
            btn.setProperty("active", "true" if active else "false")
            btn.style().unpolish(btn); btn.style().polish(btn)

        if is_admin:
            self.lbl_user.setText("USERNAME")
            self.inp_user.setPlaceholderText("Enter username")
            self.lbl_pass.setText("PASSWORD")
            self.inp_pass.setPlaceholderText("Enter password")
            self.inp_pass.setEchoMode(QLineEdit.Password)
            self.lbl_hint.setText(
                "Admin →  username: <b>admin</b>  /  password: <b>admin1234</b>"
            )
            self.lbl_hint.show()
        else:
            self.lbl_user.setText("FULL NAME")
            self.inp_user.setPlaceholderText("Enter your full name")
            self.lbl_pass.setText("STUDENT ID  (YYYY-NNNN)")
            self.inp_pass.setPlaceholderText("e.g. 2021-0001")
            self.inp_pass.setEchoMode(QLineEdit.Normal)
            self.lbl_hint.setText(
                "Student →  enter your full name and ID number"
            )
            self.lbl_hint.show()

        self.lbl_error.hide()
        self.inp_user.clear()
        self.inp_pass.clear()
        self.inp_user.setFocus()

    def do_login(self):
        username = self.inp_user.text().strip()
        password = self.inp_pass.text().strip()

        if self.role == "admin":
            if username == "admin" and password == "admin1234":
                self.login_success.emit("admin", "Administrator")
            else:
                self.show_error("Invalid admin credentials.")

        elif self.role == "student":
            with db.get_db() as conn:
                row = conn.execute(
                    "SELECT * FROM student WHERE LOWER(firstname||' '||lastname)=LOWER(?) AND id=?",
                    (username, password),
                ).fetchone()
            if row:
                name = f"{row['firstname']}.{row['lastname']}"
                self.login_success.emit("student", name)
            else:
                self.show_error("Student not found. Check your full name and ID number.")

    def show_error(self, msg: str):
        self.lbl_error.setText(msg)
        self.lbl_error.show()

    def clear(self):
        self.inp_user.clear()
        self.inp_pass.clear()
        self.lbl_error.hide()
        self.switchrole("admin")
