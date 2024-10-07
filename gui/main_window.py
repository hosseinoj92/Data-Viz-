# gui/main_window.py

import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
    QPushButton, QShortcut, QFileDialog, QListWidgetItem, QColorDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QTabWidget, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence, QIcon


from gui.general_tab import GeneralTab  # Updated import
from gui.normalization_tab import NormalizationTab  # Updated import
from gui.collapsible_sections import CollapsibleSection  # Updated import
from gui.data_handling_tab import DataHandlingTab
 #Define the exception hook

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Data Wz Pro - version 2.4.2")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon('gui/resources/icon.png'))  # Set the window icon

        self.last_directory = os.path.expanduser("~")

        self.text_color = 'black'

        # Initialize central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # Create Tab Widget
        self.tabs = QTabWidget()
        self.general_tab = GeneralTab()
        self.normalization_tab = NormalizationTab(self.general_tab)
        self.data_handling_tab = DataHandlingTab()

        
        self.tabs.addTab(self.general_tab, QIcon('gui/resources/general_icon.png'), "General")
        self.tabs.addTab(self.normalization_tab, QIcon('gui/resources/normalization_icon.png'), "Normalization")
        self.tabs.addTab(self.data_handling_tab, QIcon('gui/resources/data_icon.png'), "Data Handling")


        self.main_layout.addWidget(self.tabs)

        # Delete shortcut
        delete_shortcut = QShortcut(QKeySequence("Delete"), self)
        delete_shortcut.activated.connect(self.delete_selected_file)

    def delete_selected_file(self):
        current_tab = self.tabs.currentWidget()
        current_tab.delete_selected_file()
