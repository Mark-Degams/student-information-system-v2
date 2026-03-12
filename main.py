import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QStackedWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

import app.database as db
from app.styles import APP_STYLE
from app.windows.login import LoginView
from app.main_window import MainWindow

class AppShell(QStackedWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SSIS – Student Information System")
        self.setMinimumSize(1080, 680)
        self.resize(1300, 800)
        self.setStyleSheet(APP_STYLE)

        self._login_view = LoginView()
        self._main_win   = MainWindow()

        self.addWidget(self._login_view)  
        self.addWidget(self._main_win)    

        self._login_view.login_success.connect(self._on_login)
        self._main_win.logout_requested.connect(self._on_logout)

        self.setCurrentIndex(0)

    def _on_login(self, role: str, name: str):
        self._main_win.set_user(role, name)
        self.setCurrentIndex(1)

    def _on_logout(self):
        self._login_view.clear()
        self.setCurrentIndex(0)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("SSIS")
    app.setOrganizationName("University")

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    db.init_db()

    shell = AppShell()
    shell.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
