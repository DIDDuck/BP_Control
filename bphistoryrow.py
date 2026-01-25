from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton)
from PySide6.QtCore import Qt

class BP_History_Row(QWidget):
    def __init__(self, data: list[str], index: int, delete_measurement: function):
        super().__init__()
        self.data = data
        self.index = index
        self.delete_measurement = delete_measurement
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout()
        layout.addSpacing(50)
        self.setLayout(layout)
        
        for idx, field in enumerate(self.data):
            # print("field", field)
            widget = QLabel(field)
            widget.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            if idx != 0: widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            widget.setMaximumHeight(32)
            widget.setMinimumHeight(32)
            if idx != 0: widget.setMaximumWidth(60)
            layout.addWidget(widget)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda: self.delete_measurement(self.index))
        delete_button.setStyleSheet("border: 1px solid black; min-height: 24px; max-width: 50px; max-height: 24px; border-radius: 5px; margin-top: 5px")
        layout.addWidget(delete_button)

        layout.addSpacing(50)
        self.setMinimumHeight(40)
        # self.setStyleSheet("background-color: green") 

