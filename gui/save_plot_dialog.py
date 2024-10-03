# gui/save_plot_dialog.py

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QComboBox, QPushButton

class SavePlotDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Save Plot Options")
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Image Size Inputs
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Width (pixels):"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(100, 10000)  # Define a reasonable range
        self.width_spin.setValue(800)
        size_layout.addWidget(self.width_spin)
        
        size_layout.addWidget(QLabel("Height (pixels):"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(100, 10000)
        self.height_spin.setValue(600)
        size_layout.addWidget(self.height_spin)
        
        layout.addLayout(size_layout)
        
        # Quality Dropdown
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Quality:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Low", "Medium", "High", "Very High"])
        quality_layout.addWidget(self.quality_combo)
        layout.addLayout(quality_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def get_values(self):
        width = self.width_spin.value()
        height = self.height_spin.value()
        quality = self.quality_combo.currentText()
        return width, height, quality
