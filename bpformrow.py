from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QLineEdit, QDateTimeEdit)
from PySide6.QtCore import Qt


class BP_Form_Row(QWidget):
    def __init__(self, rowtext: str = ""):
        super().__init__()
        self.rowtext = rowtext
        self.setup_gui()

    def setup_gui(self):
        layout = QHBoxLayout()
        layout.addSpacing(50)
        layout.addWidget(QLabel(self.rowtext))
        self.texts = ["Date & Time", "DP", "SP", "HR"]

        if self.rowtext == "": # Header row for measurements
            for text in self.texts:
                label = QLabel(text)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setStyleSheet("font-size: 16px; max-width: 50px;") if not text == "Date & Time" else label.setStyleSheet("font-size: 16px; min-width: 200px; max-width: 200px")
                layout.addWidget(label)
        else:
            for text in self.texts:
                widget = QLineEdit(alignment=Qt.AlignmentFlag.AlignHCenter)
                if text == "Date & Time":
                    widget = QDateTimeEdit(alignment=Qt.AlignmentFlag.AlignHCenter)
                    widget.setAlignment(Qt.AlignmentFlag.AlignLeft)
                    widget.setStyleSheet("font-size: 14px; max-width: 200px;")
                else:
                    widget = QLineEdit(alignment=Qt.AlignmentFlag.AlignHCenter)
                    widget.setStyleSheet("font-size: 14px; max-width: 48px")  

                layout.addWidget(widget)
        layout.addSpacing(50)    
        self.setLayout(layout)