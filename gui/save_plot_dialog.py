# gui/save_plot_dialog.py

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
    QComboBox, QPushButton, QMessageBox
)
from gui.latex_compatibility_dialog import LaTeXCompatibilityDialog  # Ensure this import exists
from PyQt5.QtCore import Qt

class SavePlotDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Save Plot Options")
        self.setModal(True)
        self.init_ui()
        self.latex_options = None  # Initialize LaTeX options

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
        self.quality_combo.setCurrentText("Medium")
        quality_layout.addWidget(self.quality_combo)
        layout.addLayout(quality_layout)
        
        # LaTeX Compatibility and Help Buttons
        latex_help_layout = QHBoxLayout()
        
        # LaTeX Compatible Button
        self.latex_button = QPushButton("LaTeX Compatible")
        self.latex_button.setToolTip("Configure LaTeX compatibility settings")
        self.latex_button.clicked.connect(self.open_latex_dialog)
        latex_help_layout.addWidget(self.latex_button)
        
        # "?" Help Button
        self.help_button = QPushButton("?")
        self.help_button.setToolTip("View help information about LaTeX Compatibility")
        self.help_button.clicked.connect(self.show_help)
        latex_help_layout.addWidget(self.help_button)
        
        layout.addLayout(latex_help_layout)
        
        # Reset LaTeX Settings Button
        self.reset_latex_button = QPushButton("Reset LaTeX Settings")
        self.reset_latex_button.clicked.connect(self.reset_latex_settings)
        layout.addWidget(self.reset_latex_button)
        
        # Ensure buttons have the same width as Reset LaTeX Settings
        self.reset_latex_button.adjustSize()  # Ensure the sizeHint is updated
        fixed_width = self.reset_latex_button.sizeHint().width()
        self.latex_button.setFixedWidth(fixed_width)
        self.help_button.setFixedWidth(fixed_width)
        
        # Buttons (Save and Cancel)
        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def open_latex_dialog(self):
        dialog = LaTeXCompatibilityDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.latex_options = dialog.get_values()  # Ensure this method exists
            print(f"LaTeX options received: {self.latex_options}")
    
    def reset_latex_settings(self):
        # Reset all LaTeX options to default
        self.latex_options = None
        QMessageBox.information(self, "Reset", "LaTeX settings have been reset to default.")
    
    def get_values(self):
        width = self.width_spin.value()
        height = self.height_spin.value()
        quality = self.quality_combo.currentText()
        return width, height, quality, self.latex_options
    
    def show_help(self):
        help_text = """
        <h2>LaTeX Compatibility Guide</h2>
        <p>The LaTeX compatibility feature allows you to generate plots that seamlessly match the style and formatting of your LaTeX documents. Here's how you can use the various options to create LaTeX-compatible figures:</p>
        <ul>
            <li><b>Figure Width:</b>
                <ul>
                    <li><b>What it is:</b> Sets the width of the figure in your chosen unit.</li>
                    <li><b>How to choose:</b> Match the width to your LaTeX document's text width. For example, 6.5 inches typically matches the standard text width.</li>
                </ul>
            </li>
            <li><b>Units (inches, cm, mm, pt, textwidth fraction):</b>
                <ul>
                    <li><b>What it does:</b> Defines the unit for the figure width.</li>
                    <li><b>Examples:</b>
                        <ul>
                            <li><i>inches:</i> Set width to 6.5 inches for full text width.</li>
                            <li><i>textwidth fraction:</i> Use a fraction like 0.8 for 80% of text width.</li>
                        </ul>
                    </li>
                </ul>
            </li>
            <li><b>DPI (Dots Per Inch):</b>
                <ul>
                    <li><b>What it is:</b> Controls the resolution of the saved image.</li>
                    <li><b>Common values:</b> 150 DPI for screen, 300 DPI for print.</li>
                </ul>
            </li>
            <li><b>Font Family:</b>
                <ul>
                    <li><b>What it is:</b> Chooses the font for plot labels and titles.</li>
                    <li><b>How to choose:</b> Select a font that matches your LaTeX document, such as "Times New Roman" or "Arial".</li>
                </ul>
            </li>
            <li><b>Base Font Size (pt):</b>
                <ul>
                    <li><b>What it is:</b> Sets the base font size for text in the plot.</li>
                    <li><b>How to choose:</b> Match this to your LaTeX document's font size (e.g., 10pt, 12pt).</li>
                </ul>
            </li>
            <li><b>Title and Axis Font Sizes (pt):</b>
                <ul>
                    <li><b>What it is:</b> Controls the font size for plot titles and axis labels.</li>
                    <li><b>How to choose:</b> Typically, the title font size is larger than the axis labels for emphasis.</li>
                </ul>
            </li>
            <li><b>Use LaTeX Rendering:</b>
                <ul>
                    <li><b>What it does:</b> Enables LaTeX to render all text in the plot, ensuring consistency with your document's typography.</li>
                </ul>
            </li>
        </ul>
        <p><b>How These Settings Help:</b> By configuring these settings, your plots will visually integrate with your LaTeX documents, maintaining consistency in font styles, sizes, and overall formatting. This is especially useful for academic papers, reports, and presentations where professional appearance is crucial.</p>
        """
        QMessageBox.information(self, "LaTeX Compatibility Help", help_text)
