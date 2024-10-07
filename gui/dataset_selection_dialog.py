# dataset_selection_dialog.py

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt

class DatasetSelectionDialog(QDialog):
    def __init__(self, structure, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Datasets")
        self.structure = structure
        self.selected_datasets = []
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Instruction Label
        instruction_label = QLabel("Select the datasets to combine:")
        layout.addWidget(instruction_label)
        
        # List Widget with Checkboxes
        self.list_widget = QListWidget()
        for dataset_name in sorted(self.structure.keys()):
            item = QListWidgetItem(dataset_name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.list_widget.addItem(item)
        layout.addWidget(self.list_widget)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.ok_button)
        buttons_layout.addWidget(self.cancel_button)
        layout.addLayout(buttons_layout)
        
        # Connections
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
    
    def accept(self):
        self.selected_datasets = []
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            if item.checkState() == Qt.Checked:
                self.selected_datasets.append(item.text())
        
        if not self.selected_datasets:
            QMessageBox.warning(self, "No Datasets Selected", "Please select at least one dataset.")
            return  # Do not close the dialog
        
        super().accept()
    
    def get_selected_datasets(self):
        return self.selected_datasets
