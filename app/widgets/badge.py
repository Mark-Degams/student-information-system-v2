from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt
from pathlib import Path
from app.styles import BADGE_COLORS
import json

COLORS_FILE = Path(__file__).resolve().parent / "data" / "badge_colors.json"

def make_badge(text: str, college_code: str = None) -> QLabel:
    lbl = QLabel(text)
    lbl.setAlignment(Qt.AlignCenter)
    colors = load_badge_colors()
    bg, fg = colors.get(college_code, ("#e2e8f0", "#4a5568"))
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

def load_badge_colors() -> dict:
    colors = dict(BADGE_COLORS)  
    if COLORS_FILE.exists():
        try:
            colors.update(json.loads(COLORS_FILE.read_text()))
        except Exception:
            pass
    return colors

def save_badge_color(code: str, bg: str, fg: str):
    COLORS_FILE.parent.mkdir(parents=True, exist_ok=True)
    colors = {}
    if COLORS_FILE.exists():
        try:
            colors = json.loads(COLORS_FILE.read_text())
        except Exception:
            pass
    colors[code] = (bg, fg)
    COLORS_FILE.write_text(json.dumps(colors, indent=2))

def delete_badge_color(code: str):
    if not COLORS_FILE.exists():
        return
    try:
        colors = json.loads(COLORS_FILE.read_text())
        colors.pop(code, None)
        COLORS_FILE.write_text(json.dumps(colors, indent=2))
    except Exception:
        pass