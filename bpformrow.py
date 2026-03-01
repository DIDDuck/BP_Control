from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QLineEdit, QDateTimeEdit)
from PySide6.QtCore import Qt


class BP_Form_Row(QWidget):
    """Creates one row in results form."""

    def __init__(self, rowtext: str = ""):
        """Initialize the row.
        
        Args:
            rowtext: Optional text in the beginning of the row.
        """
        super().__init__()
        self.rowtext = rowtext
        self.row_data_widgets = []
        self.setup_gui()

    def setup_gui(self):
        """Set up the results form GUI."""

        layout = QHBoxLayout()
        layout.addSpacing(50)
        layout.addWidget(QLabel(self.rowtext))
        self.texts = ["Date & Time", "SP", "DP", "HR"]

        if self.rowtext == "": # Header row for measurements
            for text in self.texts:
                label = QLabel(text)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setStyleSheet("font-size: 16px; max-width: 50px;") if not text == "Date & Time" else label.setStyleSheet("font-size: 16px; min-width: 200px; max-width: 200px")
                layout.addWidget(label)
        else:
            for text in self.texts:
                widget = None
                if text == "Date & Time":
                    widget = QDateTimeEdit(alignment=Qt.AlignmentFlag.AlignHCenter)
                    widget.setAlignment(Qt.AlignmentFlag.AlignLeft)
                    widget.setDisplayFormat("d.M.yyyy H.mm")
                    widget.setStyleSheet("font-size: 14px; max-width: 200px;")
                    self.row_data_widgets.append(widget)
                else:
                    widget = QLineEdit(alignment=Qt.AlignmentFlag.AlignHCenter)
                    widget.setStyleSheet("font-size: 14px; max-width: 48px")  
                    self.row_data_widgets.append(widget)
                layout.addWidget(widget)
        layout.addSpacing(50)    
        self.setLayout(layout)