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

class DragDropList(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setStyleSheet("background-color: #2b2b2b; border: 2px dashed #aaa; color: white;")
        self.setFont(QFont("Arial", 10))
        self.setMinimumHeight(100)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    path = url.toLocalFile()
                    if os.path.isdir(path):
                        if not self.findItems(path, Qt.MatchFlag.MatchExactly):
                            self.addItem(path)
        event.acceptProposedAction()


class ProcessWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Process")
        self.setGeometry(200, 200, 400, 300)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.Window)

        layout = QVBoxLayout()
        self.process_window = QTextEdit()
        self.process_window.setReadOnly(True)
        self.process_progress = QProgressBar()

        bottom_layout = QHBoxLayout()
        self.pause_btn = QPushButton("Pause")
        self.abort_btn = QPushButton("Abort")
        self.close_btn = QPushButton("Close")

        self.pause_btn.clicked.connect(self.on_pause_resume)
        self.abort_btn.clicked.connect(self.on_abort)
        self.close_btn.clicked.connect(self.close)

        bottom_layout.addWidget(self.pause_btn)
        bottom_layout.addWidget(self.abort_btn)
        bottom_layout.addWidget(self.close_btn)

        layout.addWidget(self.process_window)
        layout.addWidget(self.process_progress)
        layout.addLayout(bottom_layout)
        self.setLayout(layout)

    def log_processing(self, file_list):
        for filename in file_list:
            self.process_window.append(f"processing {filename}")

    def on_abort(self):
        self.process_window.append("process aborted")
        self.close()

    def on_pause_resume(self):
        if self.pause_btn.text() == "Pause":
            self.process_window.append("process paused")
            self.pause_btn.setText("Resume")
        else:
            self.process_window.append("process resumed")
            self.pause_btn.setText("Pause")
