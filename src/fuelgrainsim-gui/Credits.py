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


class Credits(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        credits_layout = QVBoxLayout()
        self.credits_label = QLabel("Zachary Siller\nGitHub: [Link]")
        self.credits_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credits_layout.addWidget(self.credits_label)
        self.setLayout(credits_layout)