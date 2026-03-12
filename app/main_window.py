from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal
from app.styles import APP_STYLE

class MainWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SSIS – Student Information System")
        self.setMinimumSize(1080, 680)
        self.resize(1300, 800)
        self.setStyleSheet(APP_STYLE)
        self._current_page = "dashboard"
