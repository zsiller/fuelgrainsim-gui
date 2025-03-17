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


class Overview(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        overview_layout = QVBoxLayout()
        self.overview_label = QLabel("Overview of the Thrust Curve Simulator")
        self.overview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.overview_image = QLabel("[Placeholder for Image]")
        self.overview_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overview_layout.addWidget(self.overview_label)
        overview_layout.addWidget(self.overview_image)

        images_layout = QHBoxLayout()
        stock_images = ["stock1.jpg", "stock2.jpg", "stock3.jpg", "stock4.jpg"]
        for img_path in stock_images:
            label = QLabel()
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if os.path.exists(img_path):
                pixmap = QPixmap(img_path)
                pixmap = pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
                label.setPixmap(pixmap)
            else:
                label.setText(f"{img_path}\n(Not Found)")
            images_layout.addWidget(label)
        overview_layout.addLayout(images_layout)
        self.setLayout(overview_layout)
