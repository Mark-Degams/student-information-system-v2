import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QApplication
from PyQt5.QtCore    import Qt, QThread, pyqtSignal, QTimer

from app.styles import COLORS_FILE

class DBInitWorker(QThread):
    progress = pyqtSignal(int, str) 
    finished = pyqtSignal()
    needed = 1000

    def run(self):
        import random
        from faker import Faker

        self.progress.emit(5,  "Connecting to database…")

        from app.database import get_db, COLLEGES, PROGRAMS, DB_PATH
        db_exists = os.path.exists(DB_PATH)  
        fake = Faker()
        with get_db() as conn:
            self.progress.emit(15, "Creating tables…")
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

            self.progress.emit(25, "Seeding colleges…")
            conn.executemany("INSERT OR IGNORE INTO college(code,name) VALUES(?,?)", COLLEGES)

            self.progress.emit(35, "Seeding programs…")
            conn.executemany("INSERT OR IGNORE INTO program(code,name,college) VALUES(?,?,?)", PROGRAMS)

            if not db_exists:
                from app.styles import COLORS_FILE
                if COLORS_FILE.exists():
                    COLORS_FILE.write_text("{}")  
                
                prog_codes = [p[0] for p in PROGRAMS]
                genders = ["Male", "Female"]
                used = {r[0] for r in conn.execute("SELECT id FROM student")}
                rows = []
                needed = self.needed

                self.progress.emit(40, f"Generating {needed:,} student records…")
                while len(rows) < needed:
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
                    if len(rows) % 500 == 0:
                        pct = 40 + int((len(rows) / needed) * 45)
                        self.progress.emit(pct, f"Generating students… {len(rows):,} / {needed:,}")

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

class LoadingScreen(QWidget):
    ready = pyqtSignal() 

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(480, 320)
        self.center()
        self.build_ui()
        self.start_worker()

    def build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QWidget(self)
        card.setObjectName("splash_card")
        card.setStyleSheet("""
            QWidget#splash_card {
                background: #2d3748;
                border-radius: 18px;
            }
        """)
        outer.addWidget(card)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(40, 48, 40, 36)
        lay.setSpacing(0)

        logo_lbl = QLabel()
        logo_lbl.setAlignment(Qt.AlignCenter)
        logo_lbl.setTextFormat(Qt.RichText)
        logo_lbl.setText(
            "<span style=\'font-size:64px; font-weight:800; color:#ffffff;\'>SS</span>"
            "<span style=\'font-size:64px; font-weight:800; color:#90cdf4;\'>IS</span>"
        )
        lay.addWidget(logo_lbl)
        lay.addSpacing(10)

        sub = QLabel("Student Information System")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet("color: rgba(255,255,255,0.45); font-size: 13px; letter-spacing: 0.5px;")
        lay.addWidget(sub)

        lay.addStretch()

        self.status_lbl = QLabel("Starting up…")
        self.status_lbl.setAlignment(Qt.AlignCenter)
        self.status_lbl.setStyleSheet("color: rgba(255,255,255,0.55); font-size: 12px;")
        lay.addWidget(self.status_lbl)
        lay.addSpacing(10)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(6)
        self.progress.setStyleSheet("""
            QProgressBar {
                background: rgba(255,255,255,0.12);
                border: none;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a9eda, stop:1 #90cdf4);
                border-radius: 3px;
            }
        """)
        lay.addWidget(self.progress)

    def center(self):
        screen = QApplication.primaryScreen().geometry()
        self.move(
            screen.center().x() - self.width()  // 2,
            screen.center().y() - self.height() // 2,
        )

    def start_worker(self):
        self.worker = DBInitWorker()
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_progress(self, pct: int, msg: str):
        self.progress.setValue(pct)
        self.status_lbl.setText(msg)

    def on_finished(self):
        self.progress.setValue(100)
        self.status_lbl.setText("Ready!")
        QTimer.singleShot(100, self.ready.emit)

    def shutdown(self):

        if hasattr(self, "_worker") and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait(2000)