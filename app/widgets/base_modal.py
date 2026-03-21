from PyQt5.QtWidgets import QToolTip, QWidget
from PyQt5.QtCore import QEvent, QTimer

class BaseModal(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_touched = False
        self.val_timer = QTimer(self)
        self.val_timer.setSingleShot(True)
        self.val_timer.timeout.connect(self.run_validation)

    def set_field_state(self, widget, state: str, tooltip: str = ""):
        widget.setProperty("state", state)
        widget.setToolTip(tooltip)
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    def on_input_changed(self):
        self.user_touched = True
        self.save_btn.setEnabled(self.all_fields_filled())
        self.val_timer.start(300)

    def install_tooltip_filter(self, widget):
        widget.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseMove:
            tip = obj.toolTip()
            if tip:
                QToolTip.showText(event.globalPos(), tip, obj)
        return super().eventFilter(obj, event)

    def all_fields_filled(self) -> bool:
        raise NotImplementedError

    def run_validation(self):
        raise NotImplementedError