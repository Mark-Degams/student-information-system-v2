from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt
from app.styles import BADGE_COLORS


def make_badge(text: str, college_code: str = None) -> QLabel:
    lbl = QLabel(text)
    lbl.setAlignment(Qt.AlignCenter)
    bg, fg = BADGE_COLORS.get(college_code, ("#f0f0f0", "#4a5568"))
    lbl.setStyleSheet(
        f"background:{bg}; color:{fg}; border-radius:10px; "
        f"padding:2px 10px; font-size:11px; font-weight:700;"
    )
    return lbl


def badge_cell(text: str, college_code: str = None) -> QWidget:
    w   = QWidget()
    lay = QHBoxLayout(w)
    lay.setContentsMargins(8, 2, 8, 2)
    lay.setSpacing(0)
    lay.addWidget(make_badge(text, college_code))
    lay.addStretch()
    return w