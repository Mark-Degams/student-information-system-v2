from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QPainter, QBrush, QPen, QPixmap
import app.database as db

def avatar_pixmap(size=80):
    px = QPixmap(size, size)
    px.fill(Qt.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(QBrush(QColor("#e2e8f0")))
    p.setPen(Qt.NoPen)
    p.drawEllipse(0, 0, size, size)
    p.setPen(QPen(QColor("#a0aec0")))
    p.setFont(QFont("Segoe UI", size // 4))
    p.drawText(px.rect(), Qt.AlignCenter, "Photo")
    p.end()
    return px

def placeholder_label(text="No description available."):
    lbl = QLabel(text)
    lbl.setObjectName("prof_placeholder")
    lbl.setWordWrap(True)
    lbl.setAlignment(Qt.AlignTop | Qt.AlignLeft)
    return lbl

def section_title(text):
    lbl = QLabel(text)
    lbl.setObjectName("prof_section_title")
    return lbl

def mini_table(headers, rows):
    t = QTableWidget(len(rows), len(headers))
    t.setObjectName("prof_table")
    t.setHorizontalHeaderLabels(headers)
    t.setEditTriggers(QAbstractItemView.NoEditTriggers)
    t.setSelectionBehavior(QAbstractItemView.SelectRows)
    t.setShowGrid(False)
    t.setFrameShape(QFrame.NoFrame)
    t.verticalHeader().setVisible(False)
    t.verticalHeader().setDefaultSectionSize(38)
    t.horizontalHeader().setStretchLastSection(True)
    t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            item = QTableWidgetItem(str(val) if val else "—")
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            t.setItem(r, c, item)
    row_h = 38
    header_h = 36
    max_visible = 6
    visible = min(len(rows), max_visible)
    t.setFixedHeight(header_h + row_h * max(1, visible))
    return t


class StudentProfile(QWidget):
    def __init__(self, rec: dict, parent=None):
        super().__init__(parent)
        self.setFixedWidth(520)
        self.build(rec)

    def build(self, r):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 26, 28, 26)
        lay.setSpacing(16)

        top = QHBoxLayout(); top.setSpacing(18)
        avatar = QLabel(); avatar.setPixmap(avatar_pixmap(72))
        avatar.setFixedSize(72, 72)
        top.addWidget(avatar)

        info = QVBoxLayout(); info.setSpacing(4)
        name = QLabel(f"{r.get('firstname','')} {r.get('lastname','')}")
        name.setObjectName("prof_name")
        sid  = QLabel(r.get("id", ""))
        sid.setObjectName("prof_sub")
        info.addWidget(name)
        info.addWidget(sid)
        info.addStretch()
        top.addLayout(info)
        top.addStretch()
        lay.addLayout(top)

        div = QFrame(); div.setFrameShape(QFrame.HLine)
        div.setObjectName("prof_divider"); lay.addWidget(div)

        grid = QGridLayout(); grid.setSpacing(10)

        course_code = r.get("course")
        if course_code:
            college_code = db.get_college_by_program(course_code)
            course_display = f"{college_code} - {course_code}" if college_code else f"Unassigned - {course_code}"
        else:
            course_display = "Not enrolled"

        fields = [
            ("Course",     course_display),
            ("Year Level", f"Year {r.get('year', '—')}"),
            ("Gender",     r.get("gender", "—")),
        ]
        for i, (label, value) in enumerate(fields):
            lbl = QLabel(label); lbl.setObjectName("prof_field_lbl")
            val = QLabel(value); val.setObjectName("prof_field_val")
            grid.addWidget(lbl, i, 0)
            grid.addWidget(val, i, 1)
        lay.addLayout(grid)

        div2 = QFrame(); div2.setFrameShape(QFrame.HLine)
        div2.setObjectName("prof_divider"); lay.addWidget(div2)

        lay.addWidget(section_title("Description"))
        lay.addWidget(placeholder_label("No description available. Add a bio or notes for this student."))


class ProgramProfile(QWidget):
    def __init__(self, rec: dict, parent=None):
        super().__init__(parent)
        self.setFixedWidth(560)
        self.build(rec)

    def build(self, r):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 26, 28, 26)
        lay.setSpacing(16)

        top = QHBoxLayout(); top.setSpacing(18)
        avatar = QLabel(); avatar.setPixmap(avatar_pixmap(72))
        avatar.setFixedSize(72, 72)
        top.addWidget(avatar)

        info = QVBoxLayout(); info.setSpacing(4)
        name = QLabel(r.get("name", ""))
        name.setObjectName("prof_name")
        name.setWordWrap(True)
        code = QLabel(r.get("code", ""))
        code.setObjectName("prof_sub")
        college = QLabel(f"College: {r.get('college') or 'Unassigned'}")
        college.setObjectName("prof_sub")
        info.addWidget(name)
        info.addWidget(code)
        info.addWidget(college)
        info.addStretch()
        top.addLayout(info, 1)
        lay.addLayout(top)

        div = QFrame(); div.setFrameShape(QFrame.HLine)
        div.setObjectName("prof_divider"); lay.addWidget(div)

        lay.addWidget(section_title("Description"))
        lay.addWidget(placeholder_label("No description available. Add details about this program."))

        div2 = QFrame(); div2.setFrameShape(QFrame.HLine)
        div2.setObjectName("prof_divider"); lay.addWidget(div2)

        students = db.students_by_program(r["code"])
        lay.addWidget(section_title(f"Enrolled Students ({len(students)})"))
        rows = [[s["id"], s["firstname"], s["lastname"]] for s in students]
        lay.addWidget(mini_table(["ID", "First Name", "Last Name"], rows))


class CollegeProfile(QWidget):
    def __init__(self, rec: dict, parent=None):
        super().__init__(parent)
        self.setFixedWidth(560)
        self.build(rec)

    def build(self, r):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 26, 28, 26)
        lay.setSpacing(16)

        top = QHBoxLayout(); top.setSpacing(18)
        avatar = QLabel(); avatar.setPixmap(avatar_pixmap(72))
        avatar.setFixedSize(72, 72)
        top.addWidget(avatar)

        info = QVBoxLayout(); info.setSpacing(4)
        name = QLabel(r.get("name", ""))
        name.setObjectName("prof_name")
        name.setWordWrap(True)
        code = QLabel(r.get("code", ""))
        code.setObjectName("prof_sub")
        info.addWidget(name)
        info.addWidget(code)
        info.addStretch()
        top.addLayout(info, 1)
        lay.addLayout(top)

        div = QFrame(); div.setFrameShape(QFrame.HLine)
        div.setObjectName("prof_divider"); lay.addWidget(div)

        lay.addWidget(section_title("Description"))
        lay.addWidget(placeholder_label("No description available. Add details about this college."))

        div2 = QFrame(); div2.setFrameShape(QFrame.HLine)
        div2.setObjectName("prof_divider"); lay.addWidget(div2)

        programs = db.programs_by_college(r["code"])
        lay.addWidget(section_title(f"Programs ({len(programs)})"))
        rows = [[p["code"], p["name"]] for p in programs]
        lay.addWidget(mini_table(["Code", "Program Name"], rows))

class ProfileOverlay(QWidget):
    def __init__(self, parent: QWidget, content: QWidget):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(0, 0, parent.width(), parent.height())

        self.card = QFrame(self)
        self.card.setObjectName("prof_card")

        from PyQt5.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect(self.card)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 160))
        self.card.setGraphicsEffect(shadow)

        card_lay = QVBoxLayout(self.card)
        card_lay.setContentsMargins(0, 0, 0, 0)
        card_lay.addWidget(content)
        self.card.adjustSize()
        self.center()
        self.raise_()
        self.show()

    def center(self):
        x = (self.width()  - self.card.width())  // 2
        y = (self.height() - self.card.height()) // 2
        self.card.move(max(0, x), max(0, y))

    def mousePressEvent(self, event):
        if not self.card.geometry().contains(event.pos()):
            self.hide()
            self.deleteLater()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.center()