import os
import sys
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QTextEdit, QProgressBar, QListWidget, QComboBox, QTabWidget, QLineEdit,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QToolTip
)
from PyQt6.QtGui import QPixmap, QFont, QColor, QIcon
from PyQt6.QtCore import Qt
import pandas as pd
from pathlib import Path
from config import Config

from Process_Windows import DragDropList
from Results import Results
from PyQt6.QtCore import pyqtSignal
from pathlib import Path
from thrust_simulation import run_simulation

class Input(QWidget):
    update_dropdown_signal = pyqtSignal(list)
    update_list_signal = pyqtSignal(list)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.drop_items = ["select item"]
        self.results_names = ["placeholder"]
        input_layout = QHBoxLayout()
        self.process_window = None
        drag_drop_layout = QVBoxLayout()
        self.recent_files = QComboBox()
        self.recent_files.addItem("Recent Folders")
        self.recent_files.currentIndexChanged.connect(self.populate_drag_drop_from_recents)
        self.select_file_btn = QPushButton("Select DXF Folder")
        self.select_file_btn.clicked.connect(self.open_file_dialog)
        self.clear_files_btn = QPushButton("Clear Folders")
        self.clear_files_btn.clicked.connect(self.clear_drag_drop_list)
        self.drag_drop_list = DragDropList()
        drag_drop_layout.addWidget(self.recent_files)
        drag_drop_layout.addWidget(self.select_file_btn)
        drag_drop_layout.addWidget(self.clear_files_btn)
        drag_drop_layout.addWidget(self.drag_drop_list)
        input_layout.addLayout(drag_drop_layout, 1)

        fields_layout = QVBoxLayout()
        self.isp_field = QLineEdit()
        self.isp_field.setPlaceholderText("Enter ISP")
        self.isp_field.editingFinished.connect(lambda: self.lock_field(self.isp_field))
        self.a_field = QLineEdit()
        self.a_field.setPlaceholderText("Enter a")
        self.a_field.editingFinished.connect(lambda: self.lock_field(self.a_field))
        self.nn_field = QLineEdit()
        self.nn_field.setPlaceholderText("Enter nn")
        self.nn_field.editingFinished.connect(lambda: self.lock_field(self.nn_field))
        self.density_field = QLineEdit()
        self.density_field.setPlaceholderText("Enter density")
        self.density_field.editingFinished.connect(lambda: self.lock_field(self.density_field))
        self.oxidiser_flow_rate_field = QLineEdit()
        self.oxidiser_flow_rate_field.setPlaceholderText("Enter oxidiser flow rate")
        self.oxidiser_flow_rate_field.editingFinished.connect(lambda: self.lock_field(self.oxidiser_flow_rate_field))
        self.fuel_grain_length_field = QLineEdit()
        self.fuel_grain_length_field.setPlaceholderText("Enter fuel grain length")
        self.fuel_grain_length_field.editingFinished.connect(lambda: self.lock_field(self.fuel_grain_length_field))
        self.iterations = QLineEdit()
        self.iterations.setPlaceholderText("Enter iterations (10-1000)")
        self.iterations.editingFinished.connect(self.validate_iterations)
        self.fire_time_field = QLineEdit()
        self.fire_time_field.setPlaceholderText("Enter fire time (seconds)")
        self.fire_time_field.editingFinished.connect(lambda: self.lock_field(self.fire_time_field))
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setFixedSize(120, 24)
        self.edit_btn.clicked.connect(self.unlock_all_fields)
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setFixedSize(120, 24)
        self.clear_btn.clicked.connect(self.clear_all_fields)
        self.confirm_btn = QPushButton("Confirm")
        self.confirm_btn.setFixedSize(120, 24)
        self.confirm_btn.clicked.connect(self.confirm_all_fields)
        self.output_location_btn = QPushButton("Select Output Location")
        self.output_location_btn.clicked.connect(self.open_output_folder_dialog)
        self.folder_name_field = QLineEdit()
        self.folder_name_field.setPlaceholderText("Enter folder name")
        self.folder_name_field.editingFinished.connect(lambda: self.lock_field(self.folder_name_field))
        self.run_btn = QPushButton("Run")
        self.run_btn.clicked.connect(self.on_run_pressed)

        fields_layout.addWidget(self.isp_field)
        fields_layout.addWidget(self.a_field)
        fields_layout.addWidget(self.nn_field)
        fields_layout.addWidget(self.density_field)
        fields_layout.addWidget(self.oxidiser_flow_rate_field)
        fields_layout.addWidget(self.fuel_grain_length_field)
        fields_layout.addWidget(self.iterations)
        fields_layout.addWidget(self.fire_time_field)
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.edit_btn)
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addWidget(self.confirm_btn)
        fields_layout.addLayout(buttons_layout)
        fields_layout.addWidget(self.output_location_btn)
        fields_layout.addWidget(self.folder_name_field)
        fields_layout.addWidget(self.run_btn)
        input_layout.addLayout(fields_layout, 1)

        self.setLayout(input_layout)

    def open_file_dialog(self):
        folder_dialog = QFileDialog()
        folder_dialog.setFileMode(QFileDialog.FileMode.Directory)
        folder_dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        if folder_dialog.exec():
            folder_path = folder_dialog.selectedFiles()[0]
            if not self.drag_drop_list.findItems(folder_path, Qt.MatchFlag.MatchExactly):
                self.drag_drop_list.addItem(folder_path)

    def open_output_folder_dialog(self):
        folder_dialog = QFileDialog()
        folder_dialog.setFileMode(QFileDialog.FileMode.Directory)
        folder_dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        if folder_dialog.exec():
            folder_path = folder_dialog.selectedFiles()[0]
            self.output_location_btn.setText(folder_path)

    def clear_drag_drop_list(self):
        self.drag_drop_list.clear()

    def lock_field(self, field):
        if field.text().strip() == "":
            self.show_empty_field_popup()
            return
        field.setDisabled(True)

    def validate_iterations(self):
        try:
            value = int(self.iterations.text())
            if 10 <= value <= 1000:
                self.lock_field(self.iterations)
            else:
                self.show_invalid_iterations_popup()
                self.iterations.clear()
                self.iterations.setPlaceholderText("Enter iterations (10-1000)")
        except ValueError:
            self.show_invalid_iterations_popup()
            self.iterations.clear()
            self.iterations.setPlaceholderText("Enter iterations (10-1000)")

    def unlock_all_fields(self):
        self.isp_field.setDisabled(False)
        self.a_field.setDisabled(False)
        self.nn_field.setDisabled(False)
        self.density_field.setDisabled(False)
        self.oxidiser_flow_rate_field.setDisabled(False)
        self.fuel_grain_length_field.setDisabled(False)
        self.iterations.setDisabled(False)
        self.fire_time_field.setDisabled(False)
        self.folder_name_field.setDisabled(False)

    def clear_all_fields(self):
        self.isp_field.clear()
        self.a_field.clear()
        self.nn_field.clear()
        self.density_field.clear()
        self.oxidiser_flow_rate_field.clear()
        self.fuel_grain_length_field.clear()
        self.iterations.clear()
        self.fire_time_field.clear()
        self.output_location_btn.setText("Select Output Location")
        self.folder_name_field.clear()
        self.unlock_all_fields()

    def confirm_all_fields(self):
        fields = [
            self.isp_field, self.a_field, self.nn_field, self.density_field,
            self.oxidiser_flow_rate_field, self.fuel_grain_length_field, self.iterations, self.fire_time_field, self.folder_name_field
        ]
        for field in fields:
            if field.text().strip() == "":
                self.show_empty_field_popup()
                return
        self.lock_all_fields()

    def lock_all_fields(self):
        self.isp_field.setDisabled(True)
        self.a_field.setDisabled(True)
        self.nn_field.setDisabled(True)
        self.density_field.setDisabled(True)
        self.oxidiser_flow_rate_field.setDisabled(True)
        self.fuel_grain_length_field.setDisabled(True)
        self.iterations.setDisabled(True)
        self.fire_time_field.setDisabled(True)
        self.folder_name_field.setDisabled(True)

    def show_empty_field_popup(self):
        QApplication.beep()
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Empty Field")
        msg_box.setText("Please enter values for all fields before confirming.")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Close)
        msg_box.exec()

    def show_invalid_iterations_popup(self):
        QApplication.beep()
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Invalid Number")
        msg_box.setText("Please enter a valid number between 10 and 1000.")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Close)
        msg_box.exec()

    def on_run_pressed(self):
        folder_paths = [self.drag_drop_list.item(i).text() for i in range(self.drag_drop_list.count())]
        output_folder = self.output_location_btn.text()

        if not folder_paths:
            self.show_error_popup("No folders in the drag and drop area. Please add folders before pressing Run.")
            return

        if output_folder == "Select Output Location":
            self.show_error_popup("No output folder selected. Please select an output folder before pressing Run.")
            return

        fields = [
            self.isp_field, self.a_field, self.nn_field, self.density_field,
            self.oxidiser_flow_rate_field, self.fuel_grain_length_field, self.iterations, self.fire_time_field, self.output_location_btn
        ]
        for field in fields:
            if field.text().strip() == "":
                self.show_error_popup("Please enter values for all fields before pressing Run.")
                return

        self.run_btn.setText("Simulation Running...")

        for path in folder_paths:
            if self.recent_files.findText(path) == -1:
                self.recent_files.addItem(path)
        #self.results_dropdown.clear()
        #for path in folder_paths:
            #self.results_dropdown.addItem(os.path.basename(path))
        """
        if self.process_window is None or not self.process_window.isVisible():
            self.process_window = ProcessWindow(self)
            self.process_window.show()
        self.process_window.log_processing(folder_paths)
        self.drag_drop_list.clear()
        """


        # Run the Python script
        #variables = f"{self.isp_field.text()},{self.a_field.text()},{self.nn_field.text()},{self.density_field.text()},{self.oxidiser_flow_rate_field.text()},{self.fuel_grain_length_field.text()},{self.iterations.text()},{self.fire_time_field.text()}"
        folder_name = self.folder_name_field.text()
        output = Path(output_folder) / folder_name
        isp = self.isp_field.text()
        a = self.a_field.text()
        nn = self.nn_field.text()
        density = self.density_field.text()
        flow = self.oxidiser_flow_rate_field.text()
        length = self.fuel_grain_length_field.text()
        iterations = self.iterations.text()
        time = self.fire_time_field.text()

        try:
            #subprocess.run(["python", "thrust_simulation.py", "-i", folder_paths[0], "-o", folder_name, "-v", variables], check=True)
            if run_simulation(folder_paths[0], output, isp, a, nn, density, flow, length, iterations, time):
                self.show_success_popup("Simulation Complete")
                self.run_btn.setText("Run")
        except subprocess.CalledProcessError as e:
            self.show_error_popup(f"An error occurred while running the script: {e}")
            self.run_btn.setText("Run")

        files = list(Path(folder_paths[0]).glob("*.dxf"))

        for i in files:
            self.drop_items.append(str(output / i.stem))
            self.results_names.append(str(output / i.stem))
        self.update_dropdown_signal.emit(self.drop_items)
        self.update_list_signal.emit(self.results_names)

    def show_error_popup(self, message):
        QApplication.beep()
        error_msg = QMessageBox(self)
        error_msg.setWindowTitle("Error")
        error_msg.setText(message)
        error_msg.setStandardButtons(QMessageBox.StandardButton.Close)
        error_msg.exec()

    def populate_drag_drop_from_recents(self, index):
        selected_item = self.recent_files.itemText(index)
        if selected_item != "Recent Folders" and selected_item:
            if not self.drag_drop_list.findItems(selected_item, Qt.MatchFlag.MatchExactly):
                self.drag_drop_list.addItem(selected_item)

    def show_success_popup(self, message):
        success_msg = QMessageBox(self)
        success_msg.setWindowTitle("Process")
        success_msg.setText(message)
        success_msg.setStandardButtons(QMessageBox.StandardButton.Close)
        success_msg.exec()


