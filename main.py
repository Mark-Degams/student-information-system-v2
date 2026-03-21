import sys
import os
from PyQt5.QtWidgets import QApplication, QStackedWidget
from PyQt5.QtGui import QFont, QIcon, QPixmap
from pathlib import Path
from app.windows.loading import LoadingScreen

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class AppShell(QStackedWidget):

    def __init__(self):
        from app.styles import APP_STYLE
        from app.windows.login import LoginView
        from app.windows.main_window import MainWindow

        super().__init__()
        self.setWindowTitle("SSIS - Student Information System")
        self.setWindowIcon(QIcon(QPixmap(str(Path(__file__).resolve().parent/"app"/"icons"/"logo.png"))))
        self.setMinimumSize(1100, 680)
        self.resize(1100, 800)
        self.setStyleSheet(APP_STYLE)

        self.login_view = LoginView()
        self.main_win   = MainWindow()

        self.addWidget(self.login_view)  
        self.addWidget(self.main_win)    

        self.login_view.login_success.connect(self.on_login)
        self.main_win.logout_requested.connect(self.on_logout)

        self.setCurrentIndex(0)
        # self.login_view.login_success.emit("admin", "Administrator") # Auto-login for testing

    def on_login(self, role: str, name: str):
        self.main_win.set_user(role, name)
        self.setCurrentIndex(1)

    def on_logout(self):
        self.login_view.clear()
        self.setCurrentIndex(0)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("SSIS")
    app.setOrganizationName("University")

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    loading = LoadingScreen()
    loading.show()
    app.aboutToQuit.connect(loading.shutdown)

    def on_ready():
        app.shell = AppShell()
        app.shell.show()
        app.shell.activateWindow()

        loading.hide()
        loading.deleteLater()

    loading.ready.connect(on_ready)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()