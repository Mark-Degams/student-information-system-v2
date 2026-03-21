# SSIS — Student Information System

A desktop application built with **PyQt5** for managing students, programs, and colleges in an academic institution. Supports role-based access, real-time search, inline form validation, and paginated data tables.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)
![SQLite](https://img.shields.io/badge/SQLite-3-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Table of Contents

- [Features](#features)
- [Technologies](#technologies)
- [Screenshots](#screenshots)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Installation](#installation)
- [Usage](#usage)
- [Architecture Notes](#architecture-notes)
- [Badge Colors](#badge-colors)
- [License](#license)
- [Badge Colors](#badge-colors)
- [License](#license)

## Features

- **Role-based login** — Admin has full access; Student role gets read-only access to programs and colleges only
- **Dashboard** — Live stat cards showing total students, programs, colleges, unenrolled students, and unassigned programs, plus a recent enrollments table. Clicking a stat card navigates to the relevant page with a pre-filled search
- **Student management** — Add, edit, delete students with ID, name, course, year level, and gender. Course selection is filtered by college first to reduce clutter
- **Program management** — Add, edit, delete academic programs linked to a college
- **College management** — Add, edit, delete colleges with custom badge colors (background + text) per college
- **Real-time search** — 200ms debounced search across all table pages with multisearch capabilities; student page supports field-specific filtering (ID, First Name, Last Name, Course) and intersecting multiple criteria
- **Inline form validation** — 300ms debounced validation on all modal inputs with red/green border feedback and hover tooltips showing error messages. Save button is disabled until all fields are valid
- **Pagination** — 50 records per page with page range, prev/next, and go-to-page input
- **Sortable columns** — Click any column header to sort ascending/descending (except Actions, Students, Programs columns)
- **Delete confirmation modals** — Shows a list of affected related records before confirming a destructive delete
- **Drag-and-drop modals** — All modal dialogs are draggable within the window
- **Toast notifications** — Success, edit, and delete notifications appear after each action

---

## 🛠️ Technologies

- **Python 3.10+** — Core programming language
- **PyQt5** — GUI framework for desktop application
- **SQLite** — Embedded database for data persistence
- **QSS (Qt Style Sheets)** — Custom styling and theming

---

## 📸 Screenshots

*Add screenshots of the application here to showcase the UI and features.*

---

## 📁 Project Structure

```
Simple Student Information System v2/
├── LICENSE                        # MIT License
├── main.py                        # Application entry point
├── README.md                      # This documentation
├── ssis.db                        # SQLite database (auto-generated)
│
├── app/
│   ├── __init__.py
│   ├── database.py                # Database operations and queries
│   ├── styles.py                  # Global QSS stylesheet and badge color defaults
│   ├── validators.py              # Input validation logic for all forms
│   │
│   ├── data/
│   │   ├── badge_colors.json      # Custom badge color configurations
│   │   ├── db_gen.py              # Database schema initialization
│   │   └── preset_data.py         # Sample data generation utilities
│   │
│   ├── icons/                     # SVG icons for UI elements
│   │
│   ├── modals/
│   │   ├── college_modal.py       # College add/edit modal
│   │   ├── delete_modal.py        # Generic delete confirmation modal
│   │   ├── program_modal.py       # Program add/edit modal
│   │   └── student_modal.py       # Student add/edit modal
│   │
│   ├── widgets/
│   │   ├── badge.py               # College badge rendering and color management
│   │   ├── base_modal.py          # Base modal class with validation and UI logic
│   │   ├── group_modal.py         # Group operations modal
│   │   ├── modal_overlay.py       # Modal overlay wrapper for positioning
│   │   ├── notification.py        # Toast notification system
│   │   ├── pagination.py          # Pagination controls widget
│   │   └── table.py               # Data table widget with sorting and search
│   │
│   └── windows/
│       ├── college.py             # College management window
│       ├── dashboard.py           # Dashboard with statistics and recent activity
│       ├── loading.py             # Loading screen
│       ├── login.py               # Authentication window
│       ├── main_window.py         # Main application window
│       ├── program.py             # Program management window
│       └── student.py             # Student management window
```

---

## Database Schema

Three tables with foreign key relationships:

```sql
CREATE TABLE college (
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE program (
    code    TEXT PRIMARY KEY,
    name    TEXT NOT NULL,
    college TEXT REFERENCES college(code) ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE student (
    id        TEXT PRIMARY KEY,   -- format: YYYY-NNNN e.g. 2024-0001
    firstname TEXT NOT NULL,
    lastname  TEXT NOT NULL,
    course    TEXT REFERENCES program(code) ON UPDATE CASCADE ON DELETE SET NULL,
    year      INTEGER NOT NULL,
    gender    TEXT NOT NULL
);
```

- Deleting a college sets all its programs' `college` to `NULL`
- Deleting a program sets all its students' `course` to `NULL`
- Student ID must match the pattern `YYYY-NNNN`

---

## 🚀 Installation

**Requirements:** Python 3.10+

### 1. Clone the Repository
```bash
git clone https://github.com/Mark-Degams/student-information-system-v2.git
cd "Simple Student Information System v2"
```

### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install PyQt5 faker
```

### 4. Run the Application
```bash
python main.py
```

---

## 💻 Usage

### Login Credentials
- **Admin**: Username: `admin`, Password: `password`
- **Student**: Username: `student`, Password: `password` (read-only access)

### Navigation
- **Dashboard**: Overview with statistics and recent enrollments
- **Students**: Manage student records with search, add, edit, delete
- **Programs**: Manage academic programs
- **Colleges**: Manage colleges with custom badge colors

---

## Architecture Notes

### BaseModal (`app/widgets/base_modal.py`)

All add/edit modals inherit from `BaseModal` instead of `QWidget`. It provides:

- `val_timer` — a 300ms single-shot `QTimer` that triggers `run_validation()` after the user stops typing
- `_user_touched` — flag that prevents validation running on modal open, so fields start neutral
- `set_field_state(widget, state, tooltip)` — sets `state` property (`"valid"`, `"error"`, or `""`) on a widget and forces a style refresh so QSS border colors apply
- `on_input_changed()` — connected to all text inputs; enables/disables save button immediately and schedules validation
- `install_tooltip_filter(widget)` — installs a `MouseMove` event filter so tooltips follow the cursor inside the input box

Each modal implements:
- `all_fields_filled()` — quick check to enable/disable the save button without full validation
- `run_validation()` — full validation using `validators.py`, sets field states and enables save only if all pass
- `update_save_btn()` — called once on open to set initial button state

### Validators (`app/validators.py`)

All validation rules live here, separated from UI code. Each function returns a `(state, tooltip)` tuple:

| Return | Meaning |
|--------|---------|
| `(None, None)` | Field is empty — stay neutral, no color |
| `("error", "message")` | Invalid — red border, tooltip on hover |
| `("valid", "")` | Valid — green border |

### TablePage (`app/widgets/table.py`)

Base class for `StudentWin`, `ProgramWin`, and `CollegeWin`. Subclasses define:

```python
HEADERS      = ["Col1", "Col2", ...]
SORT_KEYS    = ["db_col1", "db_col2", ...]
FIXED_WIDTHS = {col_index: pixel_width, ...}
FLEX_RATIOS  = {col_index: ratio, ...}   # fills remaining space
```

### Role Restrictions

Set via `MainWindow.set_user(role, name)`:

- `"admin"` — full access to all pages and add/edit/delete actions
- `"student"` — Dashboard and Student pages hidden, Program and College pages visible but read-only (Actions column hidden, Add button hidden)

---

## Badge Colors

Each college can have a custom background and text color for its badge displayed in the Program and Student tables. Colors are saved to a local JSON file via `app/widgets/badge.py` to `app/data/badge_color.json` and persist between sessions. Defaults are defined in `app/styles.py` under `BADGE_COLORS`.

---

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

This project was created for educational purposes as part of CSC151 coursework.
