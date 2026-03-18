from email.mime import base

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPainter, QColor, QPixmap
from PyQt5.QtSvg import QSvgRenderer
from pathlib import Path
import app.database as db


class DashboardWin(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.load()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 16)
        lay.setSpacing(18)

        base = Path(__file__).resolve().parent.parent

        student_icon = QIcon(str(base / "icons/person.svg"))
        program_icon = QIcon(str(base / "icons/program.svg"))
        college_icon = QIcon(str(base / "icons/college.svg"))
        un_std_icon = self.colored_svg_icon(base / "icons/person.svg",  "#e53e3e")
        un_prog_icon = self.colored_svg_icon(base / "icons/program.svg", "#e53e3e")

        row = QHBoxLayout()
        row.setSpacing(16)

        self.card_students = self.stat_card(student_icon, "—", "Total Students")
        self.card_programs = self.stat_card(program_icon, "—", "Total Programs")
        self.card_colleges = self.stat_card(college_icon, "—", "Total Colleges")
        self.card_un_std   = self.stat_card(un_std_icon, "—", "Total Unenrolled Students", icon_is_pixmap=True)
        self.card_un_prog  = self.stat_card(un_prog_icon, "—", "Total Unassigned Programs", icon_is_pixmap=True)

        row1 = QHBoxLayout()
        row1.setSpacing(16)
        row1.addWidget(self.card_students)
        row1.addWidget(self.card_programs)
        row1.addWidget(self.card_colleges)

        row2 = QHBoxLayout()
        row2.setSpacing(16)
        row2.addWidget(self.card_un_std)
        row2.addWidget(self.card_un_prog)

        lay.addLayout(row1)
        lay.addLayout(row2)

        sec = QLabel("Recently Enrolled Students")
        sec.setStyleSheet(
            "font-size:11px; font-weight:700; color:#718096; letter-spacing:0.08em;"
        )
        lay.addWidget(sec)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["ID Number", "Name", "Course", "Year Level"]
        )

        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setShowGrid(False)
        self.table.setFrameShape(QFrame.NoFrame)

        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(44)

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        lay.addWidget(self.table, 1)

    @staticmethod
    def stat_card(icon, num: str, label: str, icon_is_pixmap=False) -> QFrame:
        card = QFrame()
        card.setObjectName("stat_card")
        card.setFrameShape(QFrame.NoFrame)

        inner = QVBoxLayout(card)
        inner.setAlignment(Qt.AlignCenter)
        inner.setSpacing(4)
        inner.setContentsMargins(20, 22, 20, 22)

        ico = QLabel()
        ico.setObjectName("stat_icon")
        ico.setAlignment(Qt.AlignCenter)
        ico.setPixmap(icon if icon_is_pixmap else icon.pixmap(32, 32)) 

        n = QLabel(num)
        n.setObjectName("stat_num")
        n.setAlignment(Qt.AlignCenter)

        lbl = QLabel(label)
        lbl.setObjectName("stat_label")
        lbl.setAlignment(Qt.AlignCenter)

        inner.addWidget(ico)
        inner.addWidget(n)
        inner.addWidget(lbl)

        card.num_lbl = n
        return card
    
    @staticmethod
    def colored_svg_icon(path, color, size=32):
        renderer = QSvgRenderer(str(path))
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), QColor(color))
        painter.end()
        return pixmap

    def load(self):
        stats = db.get_dashboard_stats()

        self.card_students.num_lbl.setText(f"{stats['students']:,}")
        self.card_programs.num_lbl.setText(f"{stats['programs']:,}")
        self.card_colleges.num_lbl.setText(f"{stats['colleges']:,}")
        self.card_un_std.num_lbl.setText(f"{stats['un_std']:,}")
        self.card_un_prog.num_lbl.setText(f"{stats['un_prog']:,}")

        recent = stats["recent"]
        self.table.setRowCount(len(recent))

        for i, r in enumerate(recent):
            values = [
                r["id"],
                r["name"],
                r["course"],
                f"Year {r['year']}"
            ]

            for j, val in enumerate(values):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.table.setItem(i, j, item)