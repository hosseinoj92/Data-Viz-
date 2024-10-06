# gui/latex_compatibility_dialog.py

from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QSpinBox, QCheckBox, QMessageBox
)
from PyQt5.QtCore import Qt

class LaTeXCompatibilityDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("LaTeX Compatibility Options")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Figure width input
        figure_width_layout = QHBoxLayout()
        figure_width_layout.addWidget(QLabel("Figure Width:"))
        self.figure_width_input = QLineEdit()
        self.figure_width_input.setPlaceholderText("e.g., 6.5")
        figure_width_layout.addWidget(self.figure_width_input)

        self.width_unit_combo = QComboBox()
        self.width_unit_combo.addItems([
            "inches", "cm", "mm", "pt", "textwidth fraction"
        ])
        figure_width_layout.addWidget(self.width_unit_combo)
        layout.addLayout(figure_width_layout)

        # DPI input
        dpi_layout = QHBoxLayout()
        dpi_layout.addWidget(QLabel("DPI:"))
        self.dpi_spinbox = QSpinBox()
        self.dpi_spinbox.setRange(72, 600)
        self.dpi_spinbox.setValue(150)
        dpi_layout.addWidget(self.dpi_spinbox)
        layout.addLayout(dpi_layout)

        # Base Font size input
        font_size_layout = QHBoxLayout()
        font_size_layout.addWidget(QLabel("Base Font Size (pt):"))
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(6, 24)
        self.font_size_spinbox.setValue(10)
        font_size_layout.addWidget(self.font_size_spinbox)
        layout.addLayout(font_size_layout)

        # Font family selection with custom input
        font_family_layout = QHBoxLayout()
        font_family_layout.addWidget(QLabel("Font Family:"))
        self.font_family_combo = QComboBox()
        self.font_family_combo.setEditable(True)  # Allow custom input

        self.font_family_combo.addItems([
            "Times New Roman",
            "Arial",
            "Verdana",
            "Cambria",
            "Tahoma",
            "DejaVu Sans",
            "Calibri",
            "Century Gothic",
            "Lucida Sans",
            "Segoe UI"
        ])

        self.font_family_combo.setCurrentText("Times New Roman")  # Set default font
        font_family_layout.addWidget(self.font_family_combo)
        layout.addLayout(font_family_layout)

        # Title Font size input
        title_font_layout = QHBoxLayout()
        title_font_layout.addWidget(QLabel("Title Font Size (pt):"))
        self.title_font_size_spinbox = QSpinBox()
        self.title_font_size_spinbox.setRange(6, 36)
        self.title_font_size_spinbox.setValue(14)
        title_font_layout.addWidget(self.title_font_size_spinbox)
        layout.addLayout(title_font_layout)

        # Axis Labels Font size input
        axis_font_layout = QHBoxLayout()
        axis_font_layout.addWidget(QLabel("Axis Labels Font Size (pt):"))
        self.axis_font_size_spinbox = QSpinBox()
        self.axis_font_size_spinbox.setRange(6, 24)
        self.axis_font_size_spinbox.setValue(12)
        axis_font_layout.addWidget(self.axis_font_size_spinbox)
        layout.addLayout(axis_font_layout)

        # LaTeX rendering checkbox
        self.use_latex_checkbox = QCheckBox("Use LaTeX Rendering")
        self.use_latex_checkbox.setChecked(True)
        layout.addWidget(self.use_latex_checkbox)

        # Buttons
        buttons_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_and_accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.apply_button)
        buttons_layout.addWidget(self.cancel_button)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def apply_and_accept(self):
        # Validate inputs
        if not self.validate_inputs():
            return
        self.accept()

    def validate_inputs(self):
        try:
            figure_width = float(self.figure_width_input.text())
            if figure_width <= 0:
                raise ValueError("Figure width must be positive.")
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid positive number for figure width.")
            return False

        # Additional validations can be added here (e.g., font sizes)
        return True

    def get_latex_options(self):
        try:
            figure_width = float(self.figure_width_input.text())
        except ValueError:
            figure_width = 6.5  # Default value if input is invalid
        width_unit = self.width_unit_combo.currentText()
        dpi = self.dpi_spinbox.value()
        base_font_size = self.font_size_spinbox.value()
        font_family = self.font_family_combo.currentText()
        title_font_size = self.title_font_size_spinbox.value()
        axis_font_size = self.axis_font_size_spinbox.value()
        use_latex = self.use_latex_checkbox.isChecked()
        return {
            'figure_width': figure_width,
            'width_unit': width_unit,
            'dpi': dpi,
            'base_font_size': base_font_size,
            'font_family': font_family,
            'title_font_size': title_font_size,
            'axis_font_size': axis_font_size,
            'use_latex': use_latex
        }
