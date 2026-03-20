from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve

class Notify(QWidget):
    TYPES = {
        "success": ("#38a169"),
        "delete":  ("#e53e3e"),
        "edit":    ("#4a6fa5"),
    }

    def __init__(self, parent, message: str, kind="success"):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedHeight(48)

        color = self.TYPES.get(kind, self.TYPES["success"])

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 18, 0)
        layout.setSpacing(10)

        msg_lbl = QLabel(message)
        msg_lbl.setTextFormat(Qt.RichText)
        msg_lbl.setStyleSheet("color: white; font-size: 13px;")

        msg_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(msg_lbl)

        self.setStyleSheet(f"""
            QWidget {{
                background: {color};
                border-radius: 20px;
                opacity: 0.95;
            }}
        """)

        self.adjustSize()
        self.setFixedWidth(self.sizeHint().width() + 28)

        self.opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity)
        self.opacity.setOpacity(0)

        self.position(parent)
        self.show()
        self.raise_()
        self.fade_in()

    def position(self, parent):
        margin = 16
        x = parent.width()  - self.width()  - margin
        y = parent.height() - self.height() - margin
        self.move(x, y)

    def fade_in(self):
        self.anim_in = QPropertyAnimation(self.opacity, b"opacity")
        self.anim_in.setDuration(250)
        self.anim_in.setStartValue(0)
        self.anim_in.setEndValue(0.95)
        self.anim_in.setEasingCurve(QEasingCurve.OutCubic)
        self.anim_in.start()
        QTimer.singleShot(2500, self.fade_out)

    def fade_out(self):
        self.anim_out = QPropertyAnimation(self.opacity, b"opacity")
        self.anim_out.setDuration(400)
        self.anim_out.setStartValue(0.95)
        self.anim_out.setEndValue(0)
        self.anim_out.setEasingCurve(QEasingCurve.InCubic)
        self.anim_out.finished.connect(self.deleteLater)
        self.anim_out.start()