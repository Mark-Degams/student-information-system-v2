"""
styles.py
Centralised Qt stylesheet and colour constants.
"""

BADGE_COLORS: dict = {
    "CCS":  ("#ebf8ff", "#2b6cb0"),
    "COED": ("#f0fff4", "#276749"),
    "COE":  ("#faf5ff", "#6b46c1"),
    "CBA":  ("#fffaf0", "#c05621"),
    "CAS":  ("#fff5f7", "#c53030"),
    "CN":   ("#e6fffa", "#285e61"),
    "CAFA": ("#fffff0", "#744210"),
    "COL":  ("#fff5f5", "#742a2a"),
}

APP_STYLE = """
/* ── GLOBAL ─────────────────────────────────────────────────── */
QMainWindow { background: #f0f2f5; }
QWidget      { font-family: 'Segoe UI', Arial, sans-serif; }

/* ── SIDEBAR ─────────────────────────────────────────────────── */
QWidget#sidebar {
    background: #2d3748;
}
QLabel#brand {
    color: #ffffff;
    font-size: 22px;
    font-weight: bold;
    padding: 18px 20px 6px 20px;
}
QWidget#user_card {
    background: rgba(255,255,255,0.09);
    border-radius: 8px;
}
QLabel#uname { color: #ffffff; font-weight: 600; font-size: 13px; }
QLabel#urole { color: rgba(255,255,255,0.45); font-size: 11px; }

QPushButton#nav_btn {
    background: transparent;
    color: rgba(255,255,255,0.72);
    border: none;
    border-left: 3px solid transparent;
    text-align: left;
    padding: 13px 22px;
    font-size: 14px;
}
QPushButton#nav_btn:hover {
    background: rgba(255,255,255,0.08);
    color: #ffffff;
}
QPushButton#nav_btn[active="true"] {
    background: #4a6fa5;
    color: #ffffff;
    border-left: 3px solid #90cdf4;
    font-weight: 600;
}
QPushButton#logout_btn {
    background: transparent;
    color: #fc8181;
    border: none;
    text-align: left;
    padding: 13px 22px;
    font-size: 14px;
}
QPushButton#logout_btn:hover { background: rgba(252,129,129,0.12); }

/* ── CONTENT AREA ────────────────────────────────────────────── */
QWidget#content_area { background: #f0f2f5; }
QFrame#card {
    background: #fffff0;
    border: 1px solid #e8e8d0;
    border-radius: 12px;
}

/* ── TOP BAR ─────────────────────────────────────────────────── */
QLineEdit#search_box {
    background: #e8eaed;
    border: none;
    border-radius: 20px;
    padding: 10px 18px 10px 40px;
    font-size: 14px;
    color: #2d3748;
    min-height: 20px;
}
QLineEdit#search_box:focus {
    background: #dde1e7;
}
QPushButton#add_btn {
    background: #38a169;
    color: white;
    border: none;
    border-radius: 20px;
    padding: 10px 22px;
    font-size: 13px;
    font-weight: 600;
    min-height: 20px;
}
QPushButton#add_btn:hover { background: #2f855a; }

/* ── TABLE ───────────────────────────────────────────────────── */
QTableWidget {
    background: transparent;
    border: none;
    gridline-color: rgba(0,0,0,0.04);
    font-size: 13px;
    color: #2d3748;
    selection-background-color: rgba(90,127,168,0.10);
    selection-color: #2d3748;
    outline: none;
}
QTableWidget::item {
    padding: 0px 14px;
    border-bottom: 1px solid rgba(0,0,0,0.04);
}
QTableWidget::item:selected {
    background: rgba(90,127,168,0.10);
    color: #2d3748;
}
QHeaderView::section {
    background: #fffff0;
    color: #718096;
    font-size: 11px;
    font-weight: 700;
    padding: 12px 14px;
    border: none;
    border-bottom: 2px solid #e8e8d0;
    text-transform: uppercase;
}
QHeaderView::section:hover { background: #f7f7e0; }
QHeaderView { background: transparent; }

QPushButton#edit_btn {
    background: #ebf8ff; color: #2b6cb0;
    border: none; border-radius: 5px;
    padding: 4px 12px; font-size: 12px; font-weight: 500;
}
QPushButton#edit_btn:hover { background: #bee3f8; }

QPushButton#del_btn {
    background: #fff5f5; color: #e53e3e;
    border: none; border-radius: 5px;
    padding: 4px 12px; font-size: 12px; font-weight: 500;
}
QPushButton#del_btn:hover { background: #fed7d7; }

QScrollBar:vertical { width: 6px; background: transparent; border: none; }
QScrollBar::handle:vertical { background: #cbd5e0; border-radius: 3px; min-height: 30px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

/* ── STAT CARDS ──────────────────────────────────────────────── */
QFrame#stat_card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
}
QLabel#stat_icon  { font-size: 26px; }
QLabel#stat_num   { font-size: 34px; font-weight: 700; color: #2d3748; }
QLabel#stat_label { font-size: 11px; color: #718096; font-weight: 600; }

/* ── PAGINATION ──────────────────────────────────────────────── */
QPushButton#page_btn {
    background: white;
    color: #2d3748;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 5px 11px;
    font-size: 13px;
    min-width: 34px;
}
QPushButton#page_btn:hover   { background: #f7fafc; }
QPushButton#page_btn:disabled { color: #cbd5e0; background: #f7fafc; }
QPushButton#page_btn[active="true"] {
    background: #4a6fa5; color: white;
    border-color: #4a6fa5; font-weight: 700;
}
QLabel#page_info { color: #718096; font-size: 13px; }

/* ── DIALOG ──────────────────────────────────────────────────── */
QDialog  { background: #ffffff; }
QLabel#dlg_title { font-size: 16px; font-weight: 700; color: #2d3748; }
QLabel#dlg_lbl   { font-size: 11px; font-weight: 700; color: #718096; }

QLineEdit#dlg_input, QComboBox#dlg_combo, QSpinBox#dlg_spin {
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 7px;
    padding: 9px 13px;
    font-size: 14px;
    color: #2d3748;
}
QLineEdit#dlg_input:focus, QComboBox#dlg_combo:focus, QSpinBox#dlg_spin:focus {
    border-color: #4a6fa5;
}
QComboBox#dlg_combo::drop-down { border: none; width: 24px; }
QComboBox#dlg_combo QAbstractItemView {
    background: white; border: 1px solid #e2e8f0;
    selection-background-color: #ebf8ff; color: #2d3748;
}
QSpinBox#dlg_spin::up-button, QSpinBox#dlg_spin::down-button { width: 18px; }

QPushButton#save_btn {
    background: #38a169; color: white; border: none;
    border-radius: 7px; padding: 10px 26px;
    font-size: 14px; font-weight: 600;
}
QPushButton#save_btn:hover   { background: #2f855a; }
QPushButton#cancel_btn {
    background: #f0f2f5; color: #718096; border: none;
    border-radius: 7px; padding: 10px 26px; font-size: 14px;
}
QPushButton#cancel_btn:hover { background: #e2e8f0; }

/* ── LOGIN ───────────────────────────────────────────────────── */
QWidget#login_bg {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #4a5568, stop:1 #2d3748);
}
QFrame#login_card {
    background: #ffffff;
    border-radius: 16px;
}
QLabel#login_title { font-size: 28px; font-weight: 700; color: #2d3748; }
QLabel#login_sub   { font-size: 13px; color: #718096; }

QPushButton#role_tab {
    background: transparent; color: #718096;
    border: none; border-radius: 7px;
    padding: 9px 16px; font-size: 13px; font-weight: 500;
}
QPushButton#role_tab[active="true"] {
    background: white; color: #2d3748;
    font-weight: 600;
}
QWidget#role_bar { background: #f0f2f5; border-radius: 9px; }

QLineEdit#login_input {
    background: white;
    border: 1.5px solid #e2e8f0;
    border-radius: 8px;
    padding: 11px 14px;
    font-size: 14px;
    color: #2d3748;
}
QLineEdit#login_input:focus { border-color: #4a6fa5; }

QPushButton#login_btn {
    background: #38a169; color: white; border: none;
    border-radius: 8px; padding: 12px;
    font-size: 15px; font-weight: 700;
}
QPushButton#login_btn:hover { background: #2f855a; }

QLabel#login_error {
    color: #e53e3e; font-size: 13px;
    background: #fff5f5;
    border-left: 3px solid #e53e3e;
    border-radius: 4px;
    padding: 7px 10px;
}
QLabel#login_hint {
    color: #718096; font-size: 12px;
    background: #f7fafc; border-radius: 7px;
    padding: 10px 14px; line-height: 1.6;
}
"""
