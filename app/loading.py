import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QApplication
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from app.db_gen import DBGenerator

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
        self.worker = DBGenerator()
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