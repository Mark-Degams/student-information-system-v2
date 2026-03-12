import sqlite3
import random
import os
from faker import Faker

fake = Faker()

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ssis.db")

COLLEGES = [
    ("CCS",  "College of Computer Studies"),
    ("CED",  "College of Education"),
    ("COE",  "College of Engineering"),
    ("CBAA",  "College of Business Administration and Accountancy"),
    ("CON",  "College of Nursing"),
    ("CASS", "College of Arts and Social Sciences"),
    ("CSM",  "College of Science and Mathematics"),
]

PROGRAMS = [
    ("BSCS",   "BS Computer Science",                    "CCS"),
    ("BSIT",   "BS Information Technology",              "CCS"),
    ("BSIS",   "BS Information Systems",                 "CCS"),
    ("BSDA",   "BS Data Analytics",                      "CCS"),
    ("BSNET",  "BS Computer Networking",                 "CCS"),
    ("BSED",   "BS Education",                           "CED"),
    ("BEED",   "Bachelor of Elementary Education",       "CED"),
    ("BPEA",   "BS Physical Education",                  "CED"),
    ("BSMATH", "BS Mathematics",                         "CED"),
    ("BSCE",   "BS Civil Engineering",                   "COE"),
    ("BSEE",   "BS Electrical Engineering",              "COE"),
    ("BSME",   "BS Mechanical Engineering",              "COE"),
    ("BSIE",   "BS Industrial Engineering",              "COE"),
    ("BSCHE",  "BS Chemical Engineering",                "COE"),
    ("BSECE",  "BS Electronics and Communications Eng.", "COE"),
    ("BSA",    "BS Accountancy",                         "CBAA"),
    ("BSBA",   "BS Business Administration",             "CBAA"),
    ("BSHRM",  "BS Hotel and Restaurant Management",     "CBAA"),
    ("BSTM",   "BS Tourism Management",                  "CBAA"),
    ("BSEM",   "BS Entrepreneurship Management",         "CBAA"),
    ("BSBAFM", "BSBA Financial Management",              "CBAA"),
    ("BSPSYCH","BS Psychology",                          "CASS"),
    ("BSBIO",  "BS Biology",                             "CASS"),
    ("ABCOMM", "AB Communication",                       "CASS"),
    ("BSSOC",  "BS Sociology",                           "CASS"),
    ("BSN",    "BS Nursing",                             "CON"),
    ("BSMID",  "BS Midwifery",                           "CON"),

]


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS college (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS program (
                code    TEXT PRIMARY KEY,
                name    TEXT NOT NULL,
                college TEXT NOT NULL,
                FOREIGN KEY (college) REFERENCES college(code)
                    ON UPDATE CASCADE ON DELETE RESTRICT
            );
            CREATE TABLE IF NOT EXISTS student (
                id        TEXT PRIMARY KEY,
                firstname TEXT NOT NULL,
                lastname  TEXT NOT NULL,
                course    TEXT NOT NULL,
                year      INTEGER NOT NULL CHECK(year BETWEEN 1 AND 4),
                gender    TEXT NOT NULL CHECK(gender IN ('Male','Female')),
                FOREIGN KEY (course) REFERENCES program(code)
                    ON UPDATE CASCADE ON DELETE RESTRICT
            );
            CREATE INDEX IF NOT EXISTS idx_student_course ON student(course);
            CREATE INDEX IF NOT EXISTS idx_student_name   ON student(lastname, firstname);
            CREATE INDEX IF NOT EXISTS idx_program_college ON program(college);
        """)
        conn.executemany("INSERT OR IGNORE INTO college(code,name) VALUES(?,?)", COLLEGES)
        conn.executemany("INSERT OR IGNORE INTO program(code,name,college) VALUES(?,?,?)", PROGRAMS)
        existing = conn.execute("SELECT COUNT(*) FROM student").fetchone()[0]
        if existing < 5000:
            _seed_students(conn, 5000 - existing)
        conn.commit()


def _seed_students(conn: sqlite3.Connection, count: int):
    prog_codes = [p[0] for p in PROGRAMS]
    genders = ["Male", "Female"]
    used = {r[0] for r in conn.execute("SELECT id FROM student")}
    rows = []
    while len(rows) < count:
        sid = f"{random.randint(2018, 2024)}-{random.randint(1, 9999):04d}"
        if sid in used:
            continue
        used.add(sid)
        rows.append((
            sid,
            fake.first_name(),
            fake.last_name(),
            random.choice(prog_codes),
            random.randint(1, 4),
            random.choice(genders),
        ))
    conn.executemany(
        "INSERT OR IGNORE INTO student(id,firstname,lastname,course,year,gender) VALUES(?,?,?,?,?,?)",
        rows,
    )


# ── DASHBOARD ─────────────────────────────────────────────────────────────────

def get_dashboard_stats() -> dict:
    with get_db() as conn:
        students = conn.execute("SELECT COUNT(*) FROM student").fetchone()[0]
        programs = conn.execute("SELECT COUNT(*) FROM program").fetchone()[0]
        colleges = conn.execute("SELECT COUNT(*) FROM college").fetchone()[0]
        recent   = conn.execute(
            "SELECT id, firstname||' '||lastname AS name, course, year "
            "FROM student ORDER BY ROWID DESC LIMIT 10"
        ).fetchall()
    return {
        "students": students,
        "programs": programs,
        "colleges": colleges,
        "recent":   [dict(r) for r in recent],
    }


# ── COLLEGE ───────────────────────────────────────────────────────────────────

def college_list(q="", sort_col="code", sort_asc=True, limit=50, offset=0):
    col_map = {"code": "c.code", "name": "c.name", "programs": "programs"}
    order   = f"{col_map.get(sort_col, 'c.code')} {'ASC' if sort_asc else 'DESC'}"
    like    = f"%{q}%"
    with get_db() as conn:
        rows  = conn.execute(
            f"SELECT c.code, c.name, COUNT(p.code) AS programs "
            f"FROM college c LEFT JOIN program p ON p.college=c.code "
            f"WHERE c.code LIKE ? OR c.name LIKE ? "
            f"GROUP BY c.code ORDER BY {order} LIMIT ? OFFSET ?",
            (like, like, limit, offset),
        ).fetchall()
        total = conn.execute(
            "SELECT COUNT(*) FROM college WHERE code LIKE ? OR name LIKE ?",
            (like, like),
        ).fetchone()[0]
    return [dict(r) for r in rows], total


def college_add(code: str, name: str):
    with get_db() as conn:
        conn.execute("INSERT INTO college(code,name) VALUES(?,?)", (code.upper(), name))
        conn.commit()


def college_update(old_code: str, code: str, name: str):
    with get_db() as conn:
        conn.execute("UPDATE college SET code=?,name=? WHERE code=?", (code.upper(), name, old_code))
        conn.commit()


def college_delete(code: str):
    with get_db() as conn:
        # Guard: check for linked programs
        count = conn.execute("SELECT COUNT(*) FROM program WHERE college=?", (code,)).fetchone()[0]
        if count:
            raise ValueError(f"Cannot delete: {count} program(s) still belong to this college.")
        conn.execute("DELETE FROM college WHERE code=?", (code,))
        conn.commit()


def get_college_codes() -> list:
    with get_db() as conn:
        return [r[0] for r in conn.execute("SELECT code FROM college ORDER BY code")]


# ── PROGRAM ───────────────────────────────────────────────────────────────────

def program_list(q="", sort_col="code", sort_asc=True, limit=50, offset=0):
    col_map = {
        "code":         "p.code",
        "name":         "p.name",
        "college":      "p.college",
        "college_name": "c.name",
        "students":     "students",
    }
    order = f"{col_map.get(sort_col, 'p.code')} {'ASC' if sort_asc else 'DESC'}"
    like  = f"%{q}%"
    with get_db() as conn:
        rows  = conn.execute(
            f"SELECT p.code, p.name, p.college, c.name AS college_name, "
            f"COUNT(s.id) AS students "
            f"FROM program p "
            f"LEFT JOIN college c ON c.code=p.college "
            f"LEFT JOIN student s ON s.course=p.code "
            f"WHERE p.code LIKE ? OR p.name LIKE ? OR c.name LIKE ? "
            f"GROUP BY p.code ORDER BY {order} LIMIT ? OFFSET ?",
            (like, like, like, limit, offset),
        ).fetchall()
        total = conn.execute(
            "SELECT COUNT(*) FROM program p LEFT JOIN college c ON c.code=p.college "
            "WHERE p.code LIKE ? OR p.name LIKE ? OR c.name LIKE ?",
            (like, like, like),
        ).fetchone()[0]
    return [dict(r) for r in rows], total


def program_add(code: str, name: str, college: str):
    with get_db() as conn:
        conn.execute("INSERT INTO program(code,name,college) VALUES(?,?,?)", (code.upper(), name, college))
        conn.commit()


def program_update(old_code: str, code: str, name: str, college: str):
    with get_db() as conn:
        conn.execute(
            "UPDATE program SET code=?,name=?,college=? WHERE code=?",
            (code.upper(), name, college, old_code),
        )
        conn.commit()


def program_delete(code: str):
    with get_db() as conn:
        count = conn.execute("SELECT COUNT(*) FROM student WHERE course=?", (code,)).fetchone()[0]
        if count:
            raise ValueError(f"Cannot delete: {count} student(s) are enrolled in this program.")
        conn.execute("DELETE FROM program WHERE code=?", (code,))
        conn.commit()


def get_program_codes() -> list:
    with get_db() as conn:
        return [r[0] for r in conn.execute("SELECT code FROM program ORDER BY code")]


# ── STUDENT ───────────────────────────────────────────────────────────────────

def student_list(q="", sort_col="id", sort_asc=True, limit=50, offset=0):
    col_map = {
        "id":        "s.id",
        "firstname": "s.firstname",
        "lastname":  "s.lastname",
        "course":    "s.course",
        "year":      "s.year",
        "gender":    "s.gender",
    }
    order = f"{col_map.get(sort_col, 's.id')} {'ASC' if sort_asc else 'DESC'}"
    like  = f"%{q}%"
    with get_db() as conn:
        rows  = conn.execute(
            f"SELECT s.id, s.firstname, s.lastname, s.course, s.year, s.gender, "
            f"p.name AS program_name, p.college AS college_code "
            f"FROM student s LEFT JOIN program p ON p.code=s.course "
            f"WHERE s.id LIKE ? OR s.firstname LIKE ? OR s.lastname LIKE ? OR s.course LIKE ? "
            f"ORDER BY {order} LIMIT ? OFFSET ?",
            (like, like, like, like, limit, offset),
        ).fetchall()
        total = conn.execute(
            "SELECT COUNT(*) FROM student s "
            "WHERE s.id LIKE ? OR s.firstname LIKE ? OR s.lastname LIKE ? OR s.course LIKE ?",
            (like, like, like, like),
        ).fetchone()[0]
    return [dict(r) for r in rows], total


def student_add(sid: str, firstname: str, lastname: str, course: str, year: int, gender: str):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO student(id,firstname,lastname,course,year,gender) VALUES(?,?,?,?,?,?)",
            (sid, firstname, lastname, course, year, gender),
        )
        conn.commit()


def student_update(old_id: str, sid: str, firstname: str, lastname: str, course: str, year: int, gender: str):
    with get_db() as conn:
        conn.execute(
            "UPDATE student SET id=?,firstname=?,lastname=?,course=?,year=?,gender=? WHERE id=?",
            (sid, firstname, lastname, course, year, gender, old_id),
        )
        conn.commit()


def student_delete(sid: str):
    with get_db() as conn:
        conn.execute("DELETE FROM student WHERE id=?", (sid,))
        conn.commit()


def validate_student_id(sid: str) -> bool:
    """Check YYYY-NNNN format."""
    import re
    return bool(re.match(r"^\d{4}-\d{4}$", sid))
