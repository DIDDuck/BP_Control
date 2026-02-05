from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QScrollArea,
    QDateTimeEdit,
)
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QPixmap
from bpformrow import BP_Form_Row
from bphistoryrow import BP_History_Row
import csv, fileinput
from datetime import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
        

class BP_Control(QWidget):
    def __init__(self):
        super().__init__()
        self.ROWTEXTS = ["", "Morning 1", "Morning 2", "Evening 1", "Evening 2"]
        self.graph_exists = False
        self.file_name = "data.csv"
        self.data = self.read_file(self.file_name)
        self.update_dataframe()

        self.setWindowTitle("Blood Pressure Control")
        self.setup_layout()
        self.setup_widgets()
        self.setLayout(self.page_layout)
        self.calculate_averages()
        self.setMinimumWidth(640)
        self.setMaximumWidth(640)
        self.setMaximumHeight(960)
        self.show()

    def setup_layout(self):
        # Page/main layout
        self.page_layout = QVBoxLayout()
        
        # Main layouts
        self.header_layout = QVBoxLayout()
        self.form_layout = QVBoxLayout()
        self.results_layout = QVBoxLayout() # Inside ScrollArea?

        # Averages layout
        self.averages_layout = QHBoxLayout()

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

        # Averages
        self.avg_label = QLabel("Averages")
        self.avg_morning = QLabel("")
        self.avg_evening = QLabel("")
        self.averages_layout.addWidget(self.avg_label)
        self.averages_layout.addWidget(self.avg_morning)
        self.averages_layout.addWidget(self.avg_evening)
        self.averages_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.averages = QWidget()
        self.averages.setLayout(self.averages_layout)
        self.page_layout.addWidget(self.averages)         

        # Show Graph Button
        graph_all_button = QPushButton("Show Data Graph")
        graph_all_button.setStyleSheet("max-width: 150px; height: 32px; margin-top: 20px; margin-left: 60px")
        graph_all_button.clicked.connect(self.plot_data)

        self.page_layout.addWidget(graph_all_button)

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
        self.calculate_averages()
        self.update_dataframe()


    def on_save_refresh_results(self, form_data: dict):
        index = len(self.data)
        for row_data in form_data.values():
            row_widget = BP_History_Row(row_data, index, self.delete_measurement)
            self.results_layout.addWidget(row_widget)
            self.data.append(row_data)
            index += 1
        self.calculate_averages()
        self.update_dataframe()
        

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
    

    def update_dataframe(self):
        self.df = pd.DataFrame(self.data)
        self.df.rename(columns={0: "Date and Time", 1: "Systolic Pressure", 2: "Diastolic Pressure", 3: "Heart Rate"}, inplace=True)


    def plot_data(self):
        plt.close("all")
        plt.figure(figsize=(9, 5))
        plt.plot(np.array(self.df["Date and Time"]), np.array(self.df["Systolic Pressure"], dtype=int), color="orange", label="Systolic Pressure")
        plt.plot(np.array(self.df["Date and Time"]), np.array(self.df["Diastolic Pressure"], dtype=int), color="blue", label="Diastolic Pressure")
        plt.plot(np.array(self.df["Date and Time"]), np.array(self.df["Heart Rate"], dtype=int), color="red", label="Heart Rate")
        plt.xticks(rotation=90)
        plt.ylabel("Pressure & HR", fontsize = 14)
        plt.ylim((50, 150))
        plt.xlabel("Date and Time", loc="center", fontsize=14)
        plt.legend(loc="upper left", fontsize = 9)
        plt.grid(True)
        plt.subplots_adjust(bottom = 0.31, top = 0.95)

        try:
            plt.savefig("graph_all.png") # Save the figure in a file
        except:
            "Failed to save graph."
            self.graph_exists = False
            return
        
        self.graph_exists = True
        if self.graph_exists: plt.show()
            

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

        cleared_data = self.save_measurements(form_data, self.file_name)
        self.on_save_refresh_results(cleared_data)

        # After saving form data, clear form
        for row in rows:
            for widget in row.row_data_widgets:
                if type(widget) == QDateTimeEdit:
                    widget.setDateTime(QDateTime(2000,1,1,0,0,0))
                else:
                    widget.clear()

    
    def save_measurements(self, data: dict, file_name: str) -> dict:
        cleared_data = {}
        try:
            with open(file_name, "a") as file:
                writer = csv.writer(file)
                for key, value in data.items():
                    if self.is_valid_data(value): # Check validity of entered data
                        writer.writerow(value)
                        cleared_data[key] = value

        except FileNotFoundError:
            print("File not found.")
        except Exception as e:
            print("Failed to save measurements.") 
            print(e)
        else:
            print("Valid measurements saved.")

        return cleared_data


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
            return

        # Remove selected widget/row
        self.data = self.data[0:line_index] + self.data[line_index + 1:] # data updated
        widget_to_remove = self.results_widget.findChildren(BP_History_Row)[line_index]
        self.results_layout.removeWidget(widget_to_remove) # remove widget from layout
        widget_to_remove.deleteLater() # delete the widget itself (not immediately but later)

        # Update results view
        children = self.results_widget.findChildren(BP_History_Row) # still includes the widget we want to remove
        self.on_delete_refresh_results(children, line_index)

    
    def calculate_averages(self):
        morning_sp = {"sum": 0, "number": 0, "avg": 0}
        morning_dp = {"sum": 0, "number": 0, "avg": 0}
        morning_hr = {"sum": 0, "number": 0, "avg": 0}
        evening_sp = {"sum": 0, "number": 0, "avg": 0}
        evening_dp = {"sum": 0, "number": 0, "avg": 0}
        evening_hr = {"sum": 0, "number": 0, "avg": 0}
        
        for row in self.data:
            # print(row[0])
            # print(time.strptime(row[0], "%d.%m.%Y %H.%M"))
            time_of_day = time.strptime(row[0], "%d.%m.%Y %H.%M")
            if time_of_day < time(hour = 12):
                morning_sp["sum"] += int(row[1])
                morning_sp["number"] += 1
                morning_dp["sum"] += int(row[2])
                morning_dp["number"] += 1
                morning_hr["sum"] += int(row[3])
                morning_hr["number"] += 1
            else:
                evening_sp["sum"] += int(row[1])
                evening_sp["number"] += 1
                evening_dp["sum"] += int(row[2])
                evening_dp["number"] += 1
                evening_hr["sum"] += int(row[3])
                evening_hr["number"] += 1

        morning_sp["avg"] = morning_sp["sum"]/morning_sp["number"] if morning_sp["number"] != 0 else 0
        morning_dp["avg"] = morning_dp["sum"]/morning_dp["number"] if morning_dp["number"] != 0 else 0
        morning_hr["avg"] = morning_hr["sum"]/morning_hr["number"] if morning_hr["number"] != 0 else 0
        evening_sp["avg"] = evening_sp["sum"]/evening_sp["number"] if evening_sp["number"] != 0 else 0
        evening_dp["avg"] = evening_dp["sum"]/evening_dp["number"] if evening_dp["number"] != 0 else 0
        evening_hr["avg"] = evening_hr["sum"]/evening_hr["number"] if evening_hr["number"] != 0 else 0
        
        self.avg_morning.setText(f"Morning BP: {morning_sp["avg"]:.1f}" + " / " + f"{morning_dp["avg"]:.1f}" + "  " + f"HR: {morning_hr["avg"]:.1f}")
        self.avg_evening.setText(f"- Evening BP: {evening_sp["avg"]:.1f}" + " / " + f"{evening_dp["avg"]:.1f}" + "  " + f"HR: {evening_hr["avg"]:.1f}")