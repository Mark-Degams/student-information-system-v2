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
    ("CHS",  "College of Health Sciences"),
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
    ("BSN",    "BS Nursing",                             "CHS"),
    ("BSMID",  "BS Midwifery",                           "CHS"),
]


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn

# --- DASHBOARD ------------------------------------------------------------------

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


# --- COLLEGE ------------------------------------------------------------------

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
        count = conn.execute("SELECT COUNT(*) FROM program WHERE college=?", (code,)).fetchone()[0]
        if count:
            raise ValueError(f"Cannot delete: {count} program(s) still belong to this college.")
        conn.execute("DELETE FROM college WHERE code=?", (code,))
        conn.commit()


def get_college_codes() -> list:
    with get_db() as conn:
        return [r[0] for r in conn.execute("SELECT code FROM college ORDER BY code")]


# --- PROGRAM ------------------------------------------------------------------

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
    
def code_exists(code: str) -> bool:
    with get_db() as conn:
        return conn.execute("SELECT 1 FROM program WHERE code=?", (code,)).fetchone() is not None


# --- STUDENT ------------------------------------------------------------------

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


def student_update(sid: str, firstname: str, lastname: str, course: str, year: int, gender: str):
    with get_db() as conn:
        conn.execute(
            "UPDATE student SET id=?,firstname=?,lastname=?,course=?,year=?,gender=? WHERE id=?",
            (sid, firstname, lastname, course, year, gender, sid),
        )
        conn.commit()


def student_delete(sid: str):
    with get_db() as conn:
        conn.execute("DELETE FROM student WHERE id=?", (sid,))
        conn.commit()


def validate_student_id(sid: str) -> bool:
    import re
    return bool(re.match(r"^\d{4}-\d{4}$", sid))
