from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QColor, QIcon
from PyQt5.QtSvg import QSvgRenderer

from pathlib import Path
from app.styles import APP_STYLE

from app.windows.dashboard import DashboardWin
from app.windows.student import StudentWin
from app.windows.program import ProgramWin
from app.windows.college import CollegeWin

from app.widgets.table import TablePage

class MainWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SSIS - Student Information System")
        self.setMinimumSize(1100, 680)
        self.resize(1100, 800)
        self.setStyleSheet(APP_STYLE)
        self.current_page = "dashboard"

        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)

        self.build_ui()

    def build_ui(self):
        root_widget = QWidget()
        self.setCentralWidget(root_widget)
        root = QHBoxLayout(root_widget)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self.build_sidebar())
        root.addWidget(self.build_content(), 1)

    def build_sidebar(self) -> QWidget:
        def colored_svg_icon(path, color, size=20):
            renderer = QSvgRenderer(str(path))
            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.GlobalColor.transparent)

            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            painter.fillRect(pixmap.rect(), QColor(color))
            painter.end()

            return QIcon(pixmap)
        
        base = Path(__file__).resolve().parent

        NAV_ITEMS = [
            ("dashboard", colored_svg_icon(base/"icons/dashboard.svg", "white"), "Dashboard"),
            ("student",   colored_svg_icon(base/"icons/person.svg", "white"), "Student"),
            ("program",   colored_svg_icon(base/"icons/program.svg", "white"), "Program"),
            ("college",   colored_svg_icon(base/"icons/college.svg", "white"), "College"),
        ]

        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(215)

        lay = QVBoxLayout(sidebar)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        brand = QLabel("SS<span style='color:#90cdf4'>IS</span>")
        brand.setObjectName("brand")
        brand.setTextFormat(Qt.RichText)
        lay.addWidget(brand)

        self.user_card = QWidget()
        self.user_card.setObjectName("user_card")

        uc = QVBoxLayout(self.user_card)
        uc.setSpacing(2)
        uc.setContentsMargins(12, 8, 12, 8)

        self.lbl_name = QLabel("—")
        self.lbl_name.setObjectName("uname")

        self.lbl_role = QLabel("—")
        self.lbl_role.setObjectName("urole")

        uc.addWidget(self.lbl_name)
        uc.addWidget(self.lbl_role)

        lay.addSpacing(8)
        lay.addWidget(self.user_card)
        lay.addSpacing(10)

        self.nav_btns: dict[str, QPushButton] = {}

        for page_id, icon, label in NAV_ITEMS:
            btn = QPushButton(label)
            btn.setObjectName("nav_btn")
            btn.setFixedHeight(48)

            btn.setIcon(icon)
            btn.setIconSize(QSize(20, 20))

            btn.clicked.connect(lambda _, pid=page_id: self.navigate(pid))

            self.nav_btns[page_id] = btn
            lay.addWidget(btn)

        lay.addStretch()

        logout_btn = QPushButton("Logout")
        logout_btn.setObjectName("logout_btn")
        logout_btn.setFixedHeight(48)
        logout_btn.setIcon(colored_svg_icon(base/"icons/logout.svg", "#fc8181"))
        logout_btn.setIconSize(QSize(20, 20))

        logout_btn.clicked.connect(self.logout_requested.emit)

        lay.addWidget(logout_btn)
        lay.addSpacing(10)

        return sidebar
    
    def search_focus_in(self, event):
        self.search_wrap.setProperty("active", "true")
        self.search_wrap.style().unpolish(self.search_wrap)
        self.search_wrap.style().polish(self.search_wrap)
        QLineEdit.focusInEvent(self.search_input, event)

    def search_focus_out(self, event):
        self.search_wrap.setProperty("active", "false")
        self.search_wrap.style().unpolish(self.search_wrap)
        self.search_wrap.style().polish(self.search_wrap)
        QLineEdit.focusOutEvent(self.search_input, event)

    def build_content(self) -> QWidget:
        content = QWidget(); content.setObjectName("content_area")
        lay = QVBoxLayout(content); lay.setContentsMargins(20, 16, 20, 20); lay.setSpacing(12)

        topbar = QHBoxLayout(); topbar.setSpacing(12)

        self.search_wrap = QWidget()
        self.search_wrap.setObjectName("search_wrap")

        sw = QHBoxLayout(self.search_wrap)
        sw.setContentsMargins(12, 0, 12, 0)
        sw.setSpacing(8)

        base = Path(__file__).resolve().parent
        icon_path = base / "icons" / "search.svg"

        search_icon = QLabel()
        search_icon.setPixmap(QIcon(str(icon_path)).pixmap(16, 16))
        search_icon.setObjectName("search_icon")

        self.search_input = QLineEdit()
        self.search_input.focusInEvent = self.search_focus_in
        self.search_input.focusOutEvent = self.search_focus_out
        self.search_input.setObjectName("search_box")
        self.search_input.setPlaceholderText("Search...")
        self.search_input.textChanged.connect(self.on_search)

        sw.addWidget(search_icon)
        sw.addWidget(self.search_input)

        self.add_btn = QPushButton("+  Add"); self.add_btn.setObjectName("add_btn")
        self.add_btn.setFixedHeight(42)
        self.add_btn.clicked.connect(self.on_add)

        topbar.addWidget(self.search_wrap, 1); topbar.addWidget(self.add_btn)
        lay.addLayout(topbar)

        card = QFrame(); card.setObjectName("card")
        card_lay = QVBoxLayout(card); card_lay.setContentsMargins(0, 0, 0, 0); card_lay.setSpacing(0)

        self.stack = QStackedWidget()
        self.dashboard_win = DashboardWin()
        self.student_win = StudentWin()
        self.program_win = ProgramWin()
        self.college_win = CollegeWin()

        self.stack.addWidget(self.dashboard_win)
        self.stack.addWidget(self.student_win)  
        self.stack.addWidget(self.program_win)     
        self.stack.addWidget(self.college_win)    

        card_lay.addWidget(self.stack)
        lay.addWidget(card, 1)
        return content

    def set_user(self, role: str, name: str):
        self.lbl_name.setText(name)
        self.lbl_role.setText(role.capitalize())

        restricted = role == "student"
        for page_id in ("program", "college"):
            self.nav_btns[page_id].setVisible(not restricted)

        self.navigate("dashboard")

    def navigate(self, page_id: str):
        self.current_page = page_id
        for pid, btn in self.nav_btns.items():
            btn.setProperty("active", "true" if pid == page_id else "false")
            btn.style().unpolish(btn); btn.style().polish(btn)

        idx_map = {"dashboard": 0, "student": 1, "program": 2, "college": 3}
        self.stack.setCurrentIndex(idx_map[page_id])

        is_dash = (page_id == "dashboard")
        self.add_btn.setVisible(not is_dash)
        self.search_wrap.setVisible(not is_dash)
        self.search_input.clear()

        if is_dash:
            self.dashboard_win.load()
        else:
            view = self.current_table_win()
            if view:
                view.refresh_columns()
                view.load()

    def on_search(self, q: str):
        self.last_search_query = q
        self.search_timer.start(200)

    def perform_search(self):
        view = self.current_table_win()
        if view:
            view.search(getattr(self, "last_search_query", ""))

    def on_add(self):
        view = self.current_table_win()
        if view:
            view.add_new()
            self.dashboard_win.load()

    def current_table_win(self):
        return {
            "student": self.student_win,
            "program": self.program_win,
            "college": self.college_win,
        }.get(self.current_page)
