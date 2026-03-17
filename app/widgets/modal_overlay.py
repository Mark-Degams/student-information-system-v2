from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFrame, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor

class ModalOverlay(QWidget):
    def __init__(self, parent: QWidget, content_widget: QWidget):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground) 
        self.setGeometry(0, 0, parent.width(), parent.height())

        self.drag_active = False
        self.drag_offset = QPoint()

        self.card = QFrame(self)
        self.card.setObjectName("modal_card")

        shadow = QGraphicsDropShadowEffect(self.card)
        shadow.setBlurRadius(32)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 180))
        self.card.setGraphicsEffect(shadow)

        card_lay = QVBoxLayout(self.card)
        card_lay.setContentsMargins(0, 0, 0, 0)
        card_lay.setSpacing(0)
        card_lay.addWidget(content_widget)
        self.card.adjustSize()

        self.center_card()

        self.card.mousePressEvent   = self.card_mouse_press
        self.card.mouseMoveEvent    = self.card_mouse_move
        self.card.mouseReleaseEvent = self.card_mouse_release

        self.raise_()
        self.show()

    def center_card(self):
        x = (self.width()  - self.card.width())  // 2
        y = (self.height() - self.card.height()) // 2
        self.card.move(max(0, x), max(0, y))

    def clamp_card(self, pos: QPoint) -> QPoint:
        max_x = max(0, self.width()  - self.card.width())
        max_y = max(0, self.height() - self.card.height())
        return QPoint(max(0, min(pos.x(), max_x)),
                      max(0, min(pos.y(), max_y)))

    def card_mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_active = True
            self.drag_offset = event.pos()

    def card_mouse_move(self, event):
        if self.drag_active:
            new_pos = self.card.pos() + event.pos() - self.drag_offset
            self.card.move(self.clamp_card(new_pos))

    def card_mouse_release(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_active = False

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.center_card()

    def close_overlay(self):
        self.hide()
        self.deleteLater()