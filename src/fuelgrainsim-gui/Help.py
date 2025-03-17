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


class Help(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        help_layout = QVBoxLayout()
        self.results_dropdown = QComboBox()
        help_layout.addWidget(self.results_dropdown)
        self.setLayout(help_layout)