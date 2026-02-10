from PySide6.QtWidgets import (
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
        self.setMinimumHeight(640)
        self.setMaximumHeight(960)
        self.show()

    def setup_layout(self):
        # Page/main layout
        self.page_layout = QVBoxLayout()
        
        # Main layouts
        self.header_layout = QVBoxLayout()
        self.form_layout = QVBoxLayout()
        self.results_layout = QVBoxLayout() # Inside ScrollArea?
        self.results_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

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
        self.avg_label = QLabel("Averages:")
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
        self.update_dataframe()
        self.calculate_averages()


    def on_save_refresh_results(self, form_data: dict):
        index = len(self.data)
        for row_data in form_data.values():
            row_widget = BP_History_Row(row_data, index, self.delete_measurement)
            self.results_layout.addWidget(row_widget)
            self.data.append(row_data)
            index += 1
        self.update_dataframe()
        self.calculate_averages()
        

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

        def check_time(dt: str):
            t = time.strptime(dt, "%d.%m.%Y %H.%M")
            if t < time(hour = 12):
                return "morning" 
            return "evening"
        
        self.df = pd.DataFrame(self.data)
        
        self.df.rename(columns={0: "Date and Time", 1: "Systolic Pressure", 2: "Diastolic Pressure", 3: "Heart Rate"}, inplace=True)

        if self.df.size == 0:
            self.df_morning = self.df
            self.df_evening = self.df
            return

        df_times = pd.DataFrame([check_time(dt) for dt in self.df["Date and Time"]], columns = ["Time"])
        df_combined = pd.concat([self.df, df_times], axis = 1)

        self.df_morning = self.df[df_combined["Time"] == "morning"]
        self.df_evening = self.df[df_combined["Time"] == "evening"]

        self.df_morning = self.df_morning.astype({"Systolic Pressure": "int32", "Diastolic Pressure": "int32", "Heart Rate": "int32"})
        self.df_evening = self.df_evening.astype({"Systolic Pressure": "int32", "Diastolic Pressure": "int32", "Heart Rate": "int32"})

        # print(self.df_morning.dtypes)


    def plot_data(self):

        if self.df.size == 0:
            return

        plt.close("all")

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize = (9, 10))

        # Graph 1 - morning
        ax1.plot(np.array(self.df_morning["Date and Time"]), np.array(self.df_morning["Systolic Pressure"], dtype=int), color="orange", label=f"Systolic Pressure (avg: {self.df_morning["Systolic Pressure"].mean():.0f})")
        ax1.plot(np.array(self.df_morning["Date and Time"]), np.array(self.df_morning["Diastolic Pressure"], dtype=int), color="blue", label=f"Diastolic Pressure (avg: {self.df_morning["Diastolic Pressure"].mean():.0f})")
        ax1.plot(np.array(self.df_morning["Date and Time"]), np.array(self.df_morning["Heart Rate"], dtype=int), color="red", label=f"Heart Rate (avg: {self.df_morning["Heart Rate"].mean():.0f})")
        ax1.set_ylim(50, 150)
        ax1.tick_params(axis="x", labelrotation = 90, labelsize = 9)
        ax1.set_xlabel("Date and Time", loc = "center", labelpad = 8.0, fontsize = 10)
        ax1.set_ylabel("Pressure & HR", fontsize = 10)
        ax1.set_title("Morning", fontsize = 14)
        ax1.legend(loc="upper left", fontsize = 8)
        ax1.grid(True)
        ax1.set_position([0.13, 0.65, 0.8, 0.3])

        # Graph 2 - evening
        ax2.plot(np.array(self.df_evening["Date and Time"]), np.array(self.df_evening["Systolic Pressure"], dtype=int), color="orange", label=f"Systolic Pressure (avg: {self.df_evening["Systolic Pressure"].mean():.0f})")
        ax2.plot(np.array(self.df_evening["Date and Time"]), np.array(self.df_evening["Diastolic Pressure"], dtype=int), color="blue", label=f"Diastolic Pressure (avg: {self.df_evening["Diastolic Pressure"].mean():.0f})")
        ax2.plot(np.array(self.df_evening["Date and Time"]), np.array(self.df_evening["Heart Rate"], dtype=int), color="red", label=f"Heart Rate (avg: {self.df_evening["Heart Rate"].mean():.0f})")
        ax2.set_ylim(50, 150)
        ax2.tick_params(axis="x", labelrotation = 90, labelsize = 9)
        ax2.set_xlabel("Date and Time", loc = "center", labelpad = 8.0, fontsize = 10)
        ax2.set_ylabel("Pressure & HR", fontsize = 10)
        ax2.set_title("Evening", fontsize = 14)
        ax2.legend(loc="upper left", fontsize = 8)
        ax2.grid(True)
        ax2.set_position([0.13, 0.17, 0.8, 0.3])

        self.graph_exists = True
        if self.graph_exists: plt.show()
            

    def read_form(self):
        # Find form row objects (remove the header row)
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
        checked_data = {}
        try:
            with open(file_name, "a") as file:
                writer = csv.writer(file)
                for key, value in data.items():
                    if self.is_valid_data(value): # Check validity of entered data
                        writer.writerow(value)
                        checked_data[key] = value

        except FileNotFoundError:
            print("File not found.")
        except Exception as e:
            print("Failed to save measurements.") 
            print(e)
        else:
            print("Valid measurements saved.")

        return checked_data


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

        # No data available
        if self.df.size == 0:
            self.avg_morning.setText("No morning data.")
            self.avg_evening.setText("No evening data.")
            return
        
        if self.df_morning.size == 0:
            morning_data = False
            self.avg_morning.setText("No morning data.")
        else:
            morning_data = True


        if self.df_evening.size == 0:
            evening_data = False
            self.avg_morning.setText("No morning data.")
        else:
            evening_data = True


        # Averages using Pandas
        if morning_data:
            self.morning_sp_avg = self.df_morning["Systolic Pressure"].mean()
            self.morning_dp_avg = self.df_morning["Diastolic Pressure"].mean()
            self.morning_hr_avg = self.df_morning["Heart Rate"].mean()

            self.avg_morning.setText(f"Morning BP: {self.morning_sp_avg:.1f}" + " / " + f"{self.morning_dp_avg:.1f}" + "  " + f"HR: {self.morning_hr_avg:.1f}")

        else:
            self.avg_morning.setText("No morning data.")

        
        if evening_data:
            self.evening_sp_avg = self.df_evening["Systolic Pressure"].mean() 
            self.evening_dp_avg = self.df_evening["Diastolic Pressure"].mean()
            self.evening_hr_avg = self.df_evening["Heart Rate"].mean()

            self.avg_evening.setText(f"- Evening BP: {self.evening_sp_avg:.1f}" + " / " + f"{self.evening_dp_avg:.1f}" + "  " + f"HR: {self.evening_hr_avg:.1f}")

        else: 
            self.avg_evening.setText("No evening data.")
        