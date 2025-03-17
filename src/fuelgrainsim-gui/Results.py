from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QComboBox, QVBoxLayout, QHBoxLayout, QPushButton,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QStackedWidget, QGridLayout
)
from PyQt6.QtGui import QPixmap, QMovie, QImage
from PyQt6.QtCore import Qt, QSize
import pandas as pd
import sys
import webbrowser


class Results(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.names = []
        self.movie = None  # Store GIF movie instance
        self.gif_file = None
        self.png_file = None
        self.csv_file = None

        # Main layout
        main_layout = QVBoxLayout()

        # Dropdown menu
        self.simulation_dropdown = QComboBox()
        self.simulation_dropdown.addItems(["No items"])
        self.simulation_dropdown.currentIndexChanged.connect(self.on_simulation_selected)
        main_layout.addWidget(self.simulation_dropdown)

        # Stacked widget to toggle between "Select file" and results
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # "Select file" placeholder
        self.placeholder_label = QLabel("Select file")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stacked_widget.addWidget(self.placeholder_label)

        # Results widget (hidden initially)
        self.results_widget = QWidget()
        results_layout = QVBoxLayout()

        # Image layout (GIF and PNG)
        image_layout = QHBoxLayout()

        # GIF Container (GIF + Button)
        self.gif_container = QWidget()
        gif_layout = QGridLayout()
        self.gif_label = QLabel()
        self.gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gif_label.mousePressEvent = self.open_gif  # Click to open
        gif_layout.addWidget(self.gif_label, 0, 0)

        # Play/Pause Button (Bottom-right)
        self.play_pause_button = QPushButton("Pause")
        self.play_pause_button.setFixedSize(60, 30)
        self.play_pause_button.clicked.connect(self.toggle_gif)
        gif_layout.addWidget(self.play_pause_button, 0, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        self.gif_container.setLayout(gif_layout)
        image_layout.addWidget(self.gif_container)

        # PNG Section
        self.png_label = QLabel()
        self.png_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.png_label.mousePressEvent = self.open_png  # Click to open
        image_layout.addWidget(self.png_label)

        results_layout.addLayout(image_layout)

        # CSV Table
        self.table_widget = QTableWidget()
        self.table_widget.mousePressEvent = self.open_csv  # Click to open in Excel
        results_layout.addWidget(self.table_widget)

        self.results_widget.setLayout(results_layout)
        self.stacked_widget.addWidget(self.results_widget)

        # Set main layout
        self.setLayout(main_layout)

    def update_simulation_list(self, new_simulations):
        """Update the dropdown with folder paths."""
        self.simulation_dropdown.clear()
        self.simulation_dropdown.addItems(new_simulations)
        self.names = new_simulations

    def load_simulation_data(self):
        """Load the GIF, PNG, and CSV from the selected folder."""
        selected_folder = self.simulation_dropdown.currentText()
        if not selected_folder or selected_folder == "No items":
            self.stacked_widget.setCurrentWidget(self.placeholder_label)
            return

        folder_path = Path(selected_folder).resolve()
        if not folder_path.exists():
            QMessageBox.critical(self, "Error", f"Folder not found:\n{selected_folder}")
            self.stacked_widget.setCurrentWidget(self.placeholder_label)
            return

        # Switch to results view
        self.stacked_widget.setCurrentWidget(self.results_widget)

        # Find GIF, PNG, and CSV files
        self.gif_file = next(folder_path.glob("*.gif"), None)
        self.png_file = next(folder_path.glob("*.png"), None)
        self.csv_file = next(folder_path.glob("*.csv"), None)

        # Fixed height for images
        fixed_height = 200

        # Load GIF with aspect ratio
        if self.gif_file:
            self.movie = QMovie(str(self.gif_file))
            if self.movie.isValid():
                self.gif_label.setMovie(self.movie)
                self.movie.start()
                width = float(self.movie.frameRect().width())
                print(width)
                height = float(self.movie.frameRect().height())
                print(height)
                ratio = fixed_height / height
                new_w = float(width * ratio)
                self.movie.setScaledSize(QSize(int(new_w), int(fixed_height)))
                # Adjust GIF size (width is smaller than PNG)
                #self.gif_label.setFixedHeight(fixed_height)
                #gif_width = fixed_height * 0.75  # Adjust aspect ratio
                #self.gif_label.setFixedWidth(int(gif_width))

                self.play_pause_button.show()
            else:
                self.gif_label.setText("Invalid GIF format")
                self.play_pause_button.hide()
        else:
            self.gif_label.setText("No GIF found")
            self.play_pause_button.hide()

        # Load PNG with aspect ratio
        if self.png_file:
            pixmap = QPixmap(str(self.png_file))
            if not pixmap.isNull():
                pixmap = pixmap.scaledToHeight(fixed_height, Qt.TransformationMode.SmoothTransformation)
                self.png_label.setPixmap(pixmap)
                self.png_label.setFixedHeight(fixed_height)
                self.png_label.setFixedWidth(pixmap.width())  # Ensure PNG keeps correct width
            else:
                self.png_label.setText("Invalid PNG format")
        else:
            self.png_label.setText("No PNG found")

        # Load CSV
        if self.csv_file:
            try:
                df = pd.read_csv(self.csv_file)
                df = df.map(lambda x: round(x, 4) if isinstance(x, (int, float)) else x)
                self.table_widget.setRowCount(df.shape[0])
                self.table_widget.setColumnCount(df.shape[1])
                self.table_widget.setHorizontalHeaderLabels(df.columns)

                for row in range(df.shape[0]):
                    for col in range(df.shape[1]):
                        item = QTableWidgetItem(str(df.iat[row, col]))
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                        self.table_widget.setItem(row, col, item)

                self.table_widget.resizeColumnsToContents()
                self.table_widget.resizeRowsToContents()
                self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            except Exception as e:
                self.table_widget.setRowCount(0)
                self.table_widget.setColumnCount(0)

    def toggle_gif(self):
        """Pause or resume the GIF animation."""
        if self.movie:
            if self.movie.state() == QMovie.MovieState.Running:
                self.movie.setPaused(True)
                self.play_pause_button.setText("Play")
            else:
                self.movie.setPaused(False)
                self.play_pause_button.setText("Pause")

    def open_gif(self, event):
        """Open the GIF file in the default viewer when clicked."""
        if self.gif_file:
            webbrowser.open(str(self.gif_file))

    def open_png(self, event):
        """Open the PNG file in the default viewer when clicked."""
        if self.png_file:
            webbrowser.open(str(self.png_file))

    def open_csv(self, event):
        """Open the CSV file in Excel when clicked."""
        if self.csv_file:
            webbrowser.open(str(self.csv_file))

    def on_simulation_selected(self, index):
        """Load simulation data when a new item is selected."""
        if index <= 0:
            self.stacked_widget.setCurrentWidget(self.placeholder_label)
            return
        self.load_simulation_data()
