from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QSpacerItem,
    QSizePolicy,
    QLayout,
)
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
        if self.rowtext == "": # Header row for measurements
            texts = ["DP", "SP", "HR"]
            for text in texts:
                label = QLabel(text)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setStyleSheet("max-width: 50px;")
                layout.addWidget(label)
        else:
            for i in range(3):
                widget = QLineEdit()
                widget.setStyleSheet("max-width: 48px")
                layout.addWidget(widget)
        layout.addSpacing(50)    
        self.setLayout(layout)
        
        

class BP_Control(QWidget):
    def __init__(self):
        super().__init__()
        self.ROWTEXTS = ["", "Morning 1", "Morning 2", "Evening 1", "Evening 2"]
        self.setup_layout()
        self.setup_widgets()
        self.setLayout(self.page_layout)
        self.setMinimumWidth(480)
        self.setMaximumWidth(480)
        self.show()

    def setup_layout(self):
        # Page/main layout
        self.page_layout = QVBoxLayout()
        
        # Main layouts
        self.header_layout = QVBoxLayout()
        self.form_layout = QVBoxLayout()
        self.results_layout = QVBoxLayout() # Inside ScrollArea?

        # Results layoput
        self.result_row_l = QHBoxLayout()

    def setup_widgets(self):
        # Header
        self.header = QLabel("Blood Pressure Control")
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header.setStyleSheet("font-size: 24px; max-height: 32px")
        self.page_layout.addWidget(self.header)

        # Form
        self.page_layout.addLayout(self.form_layout)
        # self.form_layout.addLayout(self.form_header)
        for text in self.ROWTEXTS:
            row = BP_Form_Row(text)
            row.setStyleSheet("font-size: 16px; max-height: 40px")
            self.form_layout.addWidget(row)

        save_button = QPushButton("Save Results")
        save_button.setStyleSheet("max-width: 100px; margin-top: 20px; margin-left: 60px")
        save_button.clicked.connect(self.save_results)

        self.form_layout.addWidget(save_button)
        self.form_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.form_layout.addStretch()

        # Results
        self.results_layout.addSpacerItem(QSpacerItem(20, 20, ))
        self.page_layout.addLayout(self.results_layout)


    def save_results(self):
        # For now this is just for testing to get data out of the fields in form
        print(self.form_layout.parentWidget().findChildren(BP_Form_Row)[4].findChildren(QLineEdit)[0].text()) # Prints data in Evening 2 - DP field.