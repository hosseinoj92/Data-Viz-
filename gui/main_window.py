# main_window.py

from PyQt5.QtWidgets import QMainWindow, QTabWidget
from PyQt5.QtGui import QIcon

# Import the tab classes
from gui.general_tab import GeneralTab
from gui.normalization_tab import NormalizationTab
from gui.data_handling_tab import DataHandlingTab  # Import the new DataHandlingTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Wiz Pro")
        self.setGeometry(100, 100, 1200, 800)
        
        self.init_ui()
    
    def init_ui(self):
        # Create the tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Initialize tabs
        self.general_tab = GeneralTab()
        self.normalization_tab = NormalizationTab(general_tab=self.general_tab)
        self.data_handling_tab = DataHandlingTab()
        
        # Add tabs to the tab widget with icons
        self.tabs.addTab(self.general_tab, QIcon('gui/resources/general_icon.png'), "General")
        self.tabs.addTab(self.normalization_tab, QIcon('gui/resources/normalization_icon.png'), "Normalization")
        self.tabs.addTab(self.data_handling_tab, QIcon('gui/resources/data_icon.png'), "Data Handling")
        
        # Optionally, set the default tab
        self.tabs.setCurrentWidget(self.general_tab)
