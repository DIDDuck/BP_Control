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
    QDateTimeEdit,
    QScrollArea,
    QScrollBar,
)
from PySide6.QtCore import Qt
from bpformrow import BP_Form_Row
from bphistoryrow import BP_History_Row
import csv, fileinput
        

class BP_Control(QWidget):
    def __init__(self):
        super().__init__()
        self.ROWTEXTS = ["", "Morning 1", "Morning 2", "Evening 1", "Evening 2"]
        self.file_name = "data.csv"
        self.data = self.read_file(self.file_name)

        self.setWindowTitle("Blood Pressure Control")
        self.setup_layout()
        self.setup_widgets()
        self.setLayout(self.page_layout)
        self.setMinimumWidth(640)
        self.setMaximumWidth(640)
        self.setMinimumHeight(640)
        self.setMaximumHeight(640)
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

        for text in self.ROWTEXTS:
            row = BP_Form_Row(text)
            row.setStyleSheet("font-size: 16px; max-height: 40px")
            self.form_layout.addWidget(row)

        save_button = QPushButton("Save Results")
        save_button.setStyleSheet("max-width: 100px; height: 32px; margin-top: 20px; margin-left: 60px")
        save_button.clicked.connect(self.read_form)

        self.form_layout.addWidget(save_button)
        self.form_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.form_layout.addStretch()

        # Results
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border-radius: 10px")

        results_widget = QWidget()
        results_widget.setLayout(self.results_layout)
        self.results_widget = results_widget # Provides easy access later
        scroll_area.setWidget(self.results_widget)
        
        for index, row in enumerate(self.data):
            row_widget = BP_History_Row(row, index, self.delete_measurement)
            self.results_layout.addWidget(row_widget)

        self.page_layout.addWidget(scroll_area)


    def on_delete_refresh_results(self, results: list[BP_History_Row], idx_to_remove: int):
        results = results[0:idx_to_remove] + results[idx_to_remove + 1:]
        for index, row in enumerate(self.data):
            results[index].index = index # update index number for every BP_History_Row


    def read_file(self, file_name: str) -> list[list[str]]:
        data = []
        try:
            with open(file_name, "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    data.append(row)

        except FileNotFoundError:
            print("File not found.")
        except Exception as e:
            print("Failed to load measurements.") 
            print(e)
        else:
            print("Measurement data loaded.")
        return data

    def read_form(self):
        # Find form rows (remove the header row)
        rows = self.form_layout.parentWidget().findChildren(BP_Form_Row)[1:] 
        # print(rows)
        
        form_data = {}
        for index, row in enumerate(rows):
            line_edit_fields = row.findChildren(QLineEdit)
            form_data[f"row_{index + 1}"] = []
            for field in line_edit_fields:
                form_data[f"row_{index + 1}"].append(field.text())

        # print(f"Form data: {form_data}")

        self.save_measurements(form_data, self.file_name)

    
    def save_measurements(self, data: dict, file_name: str):
        try:
            with open(file_name, "a") as file:
                writer = csv.writer(file)
                for value in data.values():
                    if self.is_valid_data(value):
                        writer.writerow(value)

        except FileNotFoundError:
            print("File not found.")
        except Exception as e:
            print("Failed to save measurements.") 
            print(e)
        else:
            print("Valid measurements saved.")


    def is_valid_data(self, value: list[str]) -> bool:
        if not all(value): # Check that every field at least has a value
            return False
        
        valid = True
        numbers = "0123456789"
        for measurement in value[1:]: # Need to have numbers in measurements fields
            for character in measurement:
                if character not in numbers:
                    return False
        return True


    def delete_measurement(self, line_index: int):
        print(f"Delete button clicked. Index number of measurement is {line_index}")

        try:
            with fileinput.input([self.file_name],  inplace = True) as f:
                for index, line in enumerate(f):
                    if index != line_index: print(line, end = "")

        except:
            print("Failed to delete measurement.")

        # Remove selected widget/row
        self.data = self.data[0:line_index] + self.data[line_index + 1:] # data updated
        widget_to_remove = self.results_widget.findChildren(BP_History_Row)[line_index]
        self.results_layout.removeWidget(widget_to_remove) # remove widget from layout
        widget_to_remove.deleteLater() # delete the widget itself (not immediately but later)

        # Update results view
        children = self.results_widget.findChildren(BP_History_Row) # still includes the widget we want to remove
        self.on_delete_refresh_results(children, line_index)