import os
import random
from PyQt5.QtCore import QThread, pyqtSignal
from faker import Faker

class DBGenerator(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal()
    needed = 5000

    def run(self):
        self.progress.emit(5, "Connecting to database…")

        from app.database import get_db, COLLEGES, PROGRAMS, DB_PATH
        from app.widgets.badge import COLORS_FILE

        db_exists = os.path.exists(DB_PATH)
        fake = Faker()

        with get_db() as conn:
            if not db_exists:
                self.progress.emit(15, "Creating tables…")
                conn.executescript("""
                    CREATE TABLE IF NOT EXISTS college (
                        code TEXT PRIMARY KEY,
                        name TEXT NOT NULL
                    );
                    CREATE TABLE IF NOT EXISTS program (
                        code    TEXT PRIMARY KEY,
                        name    TEXT NOT NULL,
                        college TEXT,
                        FOREIGN KEY (college) REFERENCES college(code)
                            ON UPDATE CASCADE ON DELETE SET NULL
                    );
                    CREATE TABLE IF NOT EXISTS student (
                        id        TEXT PRIMARY KEY,
                        firstname TEXT NOT NULL,
                        lastname  TEXT NOT NULL,
                        course    TEXT,
                        year      INTEGER NOT NULL CHECK(year BETWEEN 1 AND 5),
                        gender    TEXT NOT NULL CHECK(gender IN ('Male','Female')),
                        FOREIGN KEY (course) REFERENCES program(code)
                            ON UPDATE CASCADE ON DELETE SET NULL
                    );
                    CREATE INDEX IF NOT EXISTS idx_student_course ON student(course);
                    CREATE INDEX IF NOT EXISTS idx_student_name   ON student(lastname, firstname);
                    CREATE INDEX IF NOT EXISTS idx_program_college ON program(college);
                """)

                if COLORS_FILE.exists():
                    COLORS_FILE.write_text("{}")

                self.progress.emit(25, "Seeding colleges…")
                conn.executemany(
                    "INSERT OR IGNORE INTO college(code,name) VALUES(?,?)", COLLEGES
                )

                self.progress.emit(35, "Seeding programs…")
                conn.executemany(
                    "INSERT OR IGNORE INTO program(code,name,college) VALUES(?,?,?)", PROGRAMS
                )

                prog_codes = [p[0] for p in PROGRAMS]
                genders = ["Male", "Female"]
                used = {r[0] for r in conn.execute("SELECT id FROM student")}
                rows = []
                needed = self.needed

                self.progress.emit(40, f"Generating {needed:,} student records…")
                while len(rows) < needed:
                    year = random.randint(2018, 2025)
                    sid = f"{year}-{random.randint(1, 9999):04d}"
                    if sid in used:
                        continue
                    used.add(sid)
                    year_lvl = random.randint(1, 2026 - year)
                    if year_lvl > 5:
                        year_lvl = 5
                    rows.append((
                        sid,
                        fake.first_name(),
                        fake.last_name(),
                        random.choice(prog_codes),
                        year_lvl,
                        random.choice(genders),
                    ))
                    if len(rows) % 500 == 0:
                        pct = 40 + int((len(rows) / needed) * 45)
                        self.progress.emit(
                            pct, f"Generating students… {len(rows):,} / {needed:,}"
                        )

                self.progress.emit(87, "Saving records to database…")
                conn.executemany(
                    "INSERT OR IGNORE INTO student(id,firstname,lastname,course,year,gender)"
                    " VALUES(?,?,?,?,?,?)",
                    rows,
                )
            else:
                self.progress.emit(60, "Loading existing records…")
                self.progress.emit(80, "Verifying database…")

            self.progress.emit(95, "Finalising…")
            conn.commit()

        self.progress.emit(100, "Ready!")
        self.finished.emit()