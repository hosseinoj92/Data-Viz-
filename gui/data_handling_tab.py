# data_handling_tab.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QFileDialog, QListWidgetItem, QMessageBox,
    QCheckBox, QGroupBox, QLabel, QListWidget, QScrollArea, QSizePolicy, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# Import other necessary components
from gui.panels import SelectedDataPanel  # Import from existing panels.py
import h5py
import pandas as pd
import os

class DataHandlingTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        # Main layout with three columns
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        
        # First Column: Stacked Selected Data, H5 Handling, and Dataset Selection Panels
        first_column = QVBoxLayout()
        
        # Selected Data Panel (existing)
        self.selected_data_panel = SelectedDataPanel()
        first_column.addWidget(self.selected_data_panel)
        
        # H5 Handling Panel
        self.h5_handling_panel = H5HandlingPanel(selected_data_panel=self.selected_data_panel)
        first_column.addWidget(self.h5_handling_panel)
        
        # Dataset Selection and Export Panel
        self.dataset_selection_panel = DatasetSelectionExportPanel(selected_data_panel=self.selected_data_panel, h5_handling_panel=self.h5_handling_panel)
        first_column.addWidget(self.dataset_selection_panel)
        
        # Add the first column to the main layout
        main_layout.addLayout(first_column, 1)
        
        # Second and Third Columns: Empty Placeholders
        second_column = QVBoxLayout()
        third_column = QVBoxLayout()
        
        # Add empty widgets or placeholders
        empty_widget_2 = QWidget()
        empty_widget_3 = QWidget()
        second_column.addWidget(empty_widget_2)
        third_column.addWidget(empty_widget_3)
        
        main_layout.addLayout(second_column, 1)
        main_layout.addLayout(third_column, 1)

class H5HandlingPanel(QGroupBox):
    def __init__(self, selected_data_panel, parent=None):
        super().__init__("H5 Handling", parent)
        self.selected_data_panel = selected_data_panel
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Process Selected H5 Files Button
        self.process_selected_button = QPushButton("Process Selected H5 Files")
        self.process_selected_button.setIcon(QIcon('gui/resources/process_selected_icon.png'))  # Ensure the icon exists
        layout.addWidget(self.process_selected_button)
        
        # Process Folder H5 Files Button
        self.process_folder_button = QPushButton("Process Folder H5 Files")
        self.process_folder_button.setIcon(QIcon('gui/resources/process_folder_icon.png'))  # Ensure the icon exists
        layout.addWidget(self.process_folder_button)
        
        # Include All Subfolders Checkbox
        self.include_subfolders_checkbox = QCheckBox("Include All Subfolders")
        layout.addWidget(self.include_subfolders_checkbox)
        
        # Spacer to push widgets to the top
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Connections
        self.process_selected_button.clicked.connect(self.process_selected_h5_files)
        self.process_folder_button.clicked.connect(self.process_folder_h5_files)
    
    def process_selected_h5_files(self):
        # Get selected H5 files from the Selected Data Panel
        selected_files = self.selected_data_panel.get_selected_files()
        h5_files = [file for file in selected_files if file.endswith('.h5')]
        
        if not h5_files:
            QMessageBox.warning(self, "No H5 Files Selected", "Please select H5 files in the Selected Data panel.")
            return
        
        self.h5_files = h5_files  # Store for access in DatasetSelectionExportPanel
        self.structures = []
        
        # Check structural consistency
        for file in h5_files:
            try:
                with h5py.File(file, 'r') as h5_file:
                    structure = self.get_h5_structure(h5_file)
                    self.structures.append(structure)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to read H5 file {file}:\n{e}")
                return
        
        if not all(struct == self.structures[0] for struct in self.structures):
            QMessageBox.warning(self, "Structural Inconsistency", "The H5 files do not have the same data structure.")
            self.h5_files = []
            self.structures = []
            return
        
        QMessageBox.information(self, "Structural Consistency", "All selected H5 files have consistent structures.")
    
    def process_folder_h5_files(self):
        # Allow the user to select a folder
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder Containing H5 Files")
        if not folder_path:
            return  # User canceled
        
        include_subfolders = self.include_subfolders_checkbox.isChecked()
        h5_files = []
        
        if include_subfolders:
            # Recursively search for H5 files
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if file.endswith('.h5'):
                        h5_files.append(os.path.join(root, file))
        else:
            # Search only in the selected folder
            for file in os.listdir(folder_path):
                if file.endswith('.h5'):
                    h5_files.append(os.path.join(folder_path, file))
        
        if not h5_files:
            QMessageBox.warning(self, "No H5 Files Found", "No H5 files found in the selected folder.")
            return
        
        self.h5_files = h5_files  # Store for access in DatasetSelectionExportPanel
        self.structures = []
        
        # Check structural consistency
        for file in h5_files:
            try:
                with h5py.File(file, 'r') as h5_file:
                    structure = self.get_h5_structure(h5_file)
                    self.structures.append(structure)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to read H5 file {file}:\n{e}")
                return
        
        if not all(struct == self.structures[0] for struct in self.structures):
            QMessageBox.warning(self, "Structural Inconsistency", "The H5 files do not have the same data structure.")
            self.h5_files = []
            self.structures = []
            return
        
        QMessageBox.information(self, "Structural Consistency", "All H5 files in the selected folder have consistent structures.")
    
    def get_h5_structure(self, h5_file):
        # Recursively get the structure of the H5 file
        structure = {}
        
        def visitor(name, node):
            if isinstance(node, h5py.Dataset):
                structure[name] = node.shape  # Store dataset name and shape
        
        h5_file.visititems(visitor)
        return structure

class DatasetSelectionExportPanel(QGroupBox):
    def __init__(self, selected_data_panel, h5_handling_panel, parent=None):
        super().__init__("Dataset Selection and Export", parent)
        self.selected_data_panel = selected_data_panel
        self.h5_handling_panel = h5_handling_panel
        self.init_ui()
        self.selected_datasets = []
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Instruction Label
        instruction_label = QLabel("Select Datasets to Combine into CSV:")
        layout.addWidget(instruction_label)
        
        # Select Datasets Button
        self.select_datasets_button = QPushButton("Select Datasets")
        self.select_datasets_button.setIcon(QIcon('gui/resources/select_datasets_icon.png'))  # Ensure the icon exists
        layout.addWidget(self.select_datasets_button)
        
        # Combine and Export Button
        self.combine_export_button = QPushButton("Combine and Export")
        self.combine_export_button.setIcon(QIcon('gui/resources/combine_export_icon.png'))  # Ensure the icon exists
        self.combine_export_button.setEnabled(False)  # Disabled until datasets are selected
        layout.addWidget(self.combine_export_button)
        
        # Add to Selected Data Panel Checkbox
        self.add_to_selected_checkbox = QCheckBox("Add CSV to Selected Data Panel")
        self.add_to_selected_checkbox.setChecked(True)
        layout.addWidget(self.add_to_selected_checkbox)
        
        # Spacer
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Connections
        self.select_datasets_button.clicked.connect(self.open_dataset_selection_dialog)
        self.combine_export_button.clicked.connect(self.combine_and_export_datasets)
    
    def open_dataset_selection_dialog(self):
        # Ensure that H5 files have been processed
        if not hasattr(self.h5_handling_panel, 'h5_files') or not self.h5_handling_panel.h5_files:
            QMessageBox.warning(self, "No H5 Files Processed", "Please process H5 files before selecting datasets.")
            return
        
        # Use the structure from the first H5 file (since all are consistent)
        structure = self.h5_handling_panel.structures[0]
        
        # Show the structure and get selected datasets
        selected_datasets = self.show_structure_and_get_datasets(structure)
        if selected_datasets:
            self.selected_datasets = selected_datasets
            self.combine_export_button.setEnabled(True)
        else:
            self.selected_datasets = []
            self.combine_export_button.setEnabled(False)
    
    def show_structure_and_get_datasets(self, structure):
        # Display the structure and allow the user to select datasets
        dialog = DatasetSelectionDialog(structure, self)
        if dialog.exec_() == QDialog.Accepted:
            selected_datasets = dialog.get_selected_datasets()
            return selected_datasets
        else:
            return []
    
    def combine_and_export_datasets(self):
        if not self.selected_datasets:
            QMessageBox.warning(self, "No Datasets Selected", "Please select at least one dataset to combine.")
            return
        
        # Get H5 files to process
        h5_files = self.h5_handling_panel.h5_files
        if not h5_files:
            QMessageBox.warning(self, "No H5 Files Processed", "Please process H5 files before exporting datasets.")
            return
        
        # Initialize list to store CSV file paths
        csv_files = []
        
        # Process each H5 file
        for file in h5_files:
            try:
                with h5py.File(file, 'r') as h5_file:
                    data = self.extract_datasets(h5_file, self.selected_datasets)
                
                # Combine datasets into a single CSV
                combined_csv = self.combine_datasets_to_csv(data, file)
                csv_files.append(combined_csv)
                
                # If add to selected data panel is checked, add CSV to the panel
                if self.add_to_selected_checkbox.isChecked():
                    self.selected_data_panel.add_file_to_panel(combined_csv)
                
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to process H5 file {file}:\n{e}")
                continue  # Proceed to next file
        
        if csv_files:
            QMessageBox.information(self, "Export Complete", "Selected datasets have been combined and exported as CSV files.")
            # Optionally, select the CSV files in the Selected Data panel
            # self.selected_data_panel.select_files(csv_files)  # This could be implemented
        else:
            QMessageBox.warning(self, "No CSV Created", "No CSV files were created.")
    
    def extract_datasets(self, h5_file, datasets):
        # Extract selected datasets
        data = {}
        for dataset_name in datasets:
            data[dataset_name] = h5_file[dataset_name][:]
        return data
    
    def combine_datasets_to_csv(self, data, h5_file_path):
        # Combine datasets into a DataFrame
        df = pd.DataFrame()
        for dataset_name, values in data.items():
            # Handle datasets based on dimensions
            if values.ndim == 1:
                df[dataset_name] = values
            elif values.ndim == 2:
                # For 2D datasets, flatten columns
                for i in range(values.shape[1]):
                    col_name = f"{dataset_name}_{i}"
                    df[col_name] = values[:, i]
            else:
                # Skip datasets with higher dimensions
                continue
        
        # Define the CSV file path
        base_name = os.path.splitext(os.path.basename(h5_file_path))[0]
        csv_file_name = f"{base_name}_combined.csv"
        csv_file_path = os.path.join(os.path.dirname(h5_file_path), csv_file_name)
        
        # Save DataFrame to CSV
        df.to_csv(csv_file_path, index=False)
        return csv_file_path

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
