import sqlite3
import os
from faker import Faker

fake = Faker()

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ssis.db")

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
        un_std = conn.execute("SELECT COUNT(*) FROM student WHERE course IS NULL").fetchone()[0]
        un_prog = conn.execute("SELECT COUNT(*) FROM program WHERE college IS NULL").fetchone()[0]
        recent   = conn.execute(
            "SELECT id, firstname||' '||lastname AS name, course, year "
            "FROM student ORDER BY ROWID DESC LIMIT 10"
        ).fetchall()
    return {
        "students": students,
        "programs": programs,
        "colleges": colleges,
        "un_std": un_std,
        "un_prog": un_prog,
        "recent":   [dict(r) for r in recent],
    }


# --- COLLEGE ------------------------------------------------------------------

def college_list(q="", sort_col="code", sort_asc=True, limit=50, offset=0):
    col_map = {"code": "c.code", "name": "c.name", "programs": "programs"}
    order = f"{col_map.get(sort_col, 'c.code')} {'ASC' if sort_asc else 'DESC'}, c.code ASC"
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
        conn.execute("UPDATE program SET college=NULL WHERE college=?", (code,))
        conn.execute("DELETE FROM college WHERE code=?", (code,))
        conn.commit()

def get_college_codes() -> list:
    with get_db() as conn:
        return [r[0] for r in conn.execute("SELECT code FROM college ORDER BY code")]
    
def college_code_exists(code: str) -> bool:
    with get_db() as conn:
        return conn.execute("SELECT 1 FROM college WHERE code=?", (code,)).fetchone() is not None


# --- PROGRAM ------------------------------------------------------------------

def program_list(q="", sort_col="code", sort_asc=True, limit=50, offset=0):
    col_map = {
        "code":         "p.code",
        "name":         "p.name",
        "college":      "p.college",
        "college_name": "c.name",
        "students":     "students",
    }
    order = f"{col_map.get(sort_col, 'p.code')} {'ASC' if sort_asc else 'DESC'}, p.code ASC"
    like  = f"%{q}%"
    with get_db() as conn:
        null_search = q.strip().lower() in ("null", "none", "n/a", "unassigned")
        if null_search:
            rows = conn.execute(
                f"SELECT p.code, p.name, p.college, c.name AS college_name, "
                f"COUNT(s.id) AS students "
                f"FROM program p "
                f"LEFT JOIN college c ON c.code=p.college "
                f"LEFT JOIN student s ON s.course=p.code "
                f"WHERE p.college IS NULL "
                f"GROUP BY p.code ORDER BY {order} LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
            total = conn.execute(
                "SELECT COUNT(*) FROM program WHERE college IS NULL"
            ).fetchone()[0]
        else:
            rows = conn.execute(
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
        conn.execute("INSERT INTO program(code,name,college) VALUES(?,?,?)", (code, name, college))
        conn.commit()

def program_update(old_code: str, code: str, name: str, college: str):
    with get_db() as conn:
        conn.execute(
            "UPDATE program SET code=?,name=?,college=? WHERE code=?",
            (code, name, college, old_code),
        )
        conn.commit()

def program_delete(code: str):
    with get_db() as conn:
        conn.execute("UPDATE student SET course=NULL WHERE course=?", (code,))
        conn.execute("DELETE FROM program WHERE code=?", (code,))
        conn.commit()

def get_program_codes() -> list:
    with get_db() as conn:
        return [r[0] for r in conn.execute("SELECT code FROM program ORDER BY code")]
    
def program_code_exists(code: str) -> bool:
    with get_db() as conn:
        return conn.execute("SELECT 1 FROM program WHERE code=?", (code,)).fetchone() is not None
    
def programs_by_college(college_code: str) -> list:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT code, name FROM program WHERE college=? ORDER BY code",
            (college_code,)
        ).fetchall()
    return [dict(r) for r in rows]

def get_program_codes_by_college(college: str) -> list:
    with get_db() as conn:
        return [r[0] for r in conn.execute(
            "SELECT code FROM program WHERE college=? ORDER BY code",
            (college,)
        )]

def get_programs_with_college() -> list:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT code, college FROM program ORDER BY code"
        ).fetchall()
    return [dict(r) for r in rows]


# --- STUDENT ------------------------------------------------------------------

def student_list(q="", sort_col="id", sort_asc=True, limit=50, offset=0, field="All Fields"):
    col_map = {
        "id":        "s.id",
        "firstname": "s.firstname",
        "lastname":  "s.lastname",
        "course":    "s.course",
        "year":      "s.year",
        "gender":    "s.gender",
    }
    primary = col_map.get(sort_col, 's.id')
    order = f"{primary} {'ASC' if sort_asc else 'DESC'}, s.id ASC"
    with get_db() as conn:
        null_search = q.strip().lower() in ("null", "none", "no course", "unenrolled")
        if null_search:
            rows = conn.execute(
                f"SELECT s.id, s.firstname, s.lastname, s.course, s.year, s.gender, "
                f"p.name AS program_name, p.college AS college_code "
                f"FROM student s LEFT JOIN program p ON p.code=s.course "
                f"WHERE s.course IS NULL "
                f"ORDER BY {order} LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
            total = conn.execute(
                "SELECT COUNT(*) FROM student WHERE course IS NULL"
            ).fetchone()[0]
        else:
            field_map = {
                "ID":         ["s.id"],
                "First Name": ["s.firstname"],
                "Last Name":  ["s.lastname"],
                "Course":     ["s.course"],
            }
            search_cols = field_map.get(field, ["s.id", "s.firstname", "s.lastname", "s.course"])
            
            terms = [t.strip() for t in q.split(" ") if t.strip()]
            if not terms:
                terms = [""]

            year_terms = [t for t in terms if t.isdigit() and 1 <= int(t) <= 5]
            other_terms = [t for t in terms if not (t.isdigit() and 1 <= int(t) <= 5)]

            term_conditions = []
            params = []
            for term in other_terms:
                col_conditions = " OR ".join(f"{c} LIKE ?" for c in search_cols)
                term_conditions.append(f"({col_conditions})")
                params.extend([f"%{term}%"] * len(search_cols))

            if year_terms:
                year_placeholders = ",".join("?" * len(year_terms))
                term_conditions.append(f"s.year IN ({year_placeholders})")
                params.extend([int(t) for t in year_terms])

            where = " AND ".join(term_conditions) if term_conditions else "1=1"

            rows = conn.execute(
                f"SELECT s.id, s.firstname, s.lastname, s.course, s.year, s.gender, "
                f"p.name AS program_name, p.college AS college_code "
                f"FROM student s LEFT JOIN program p ON p.code=s.course "
                f"WHERE {where} "
                f"ORDER BY {order} LIMIT ? OFFSET ?",
                (*params, limit, offset),
            ).fetchall()
            total = conn.execute(
                f"SELECT COUNT(*) FROM student s WHERE {where}",
                params,
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

def students_by_program(program_code: str) -> list:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, firstname, lastname FROM student WHERE course=? ORDER BY id",
            (program_code,)
        ).fetchall()
    return [dict(r) for r in rows]