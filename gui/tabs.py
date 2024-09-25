# gui/tabs.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel
from gui.panels import (
    SelectedDataPanel, AxisDetailsPanel, AdditionalTextPanel,
    CustomAnnotationsPanel, PlotVisualsPanel, PlotDetailsPanel
)
from PyQt5.QtCore import Qt

class GeneralTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.layout = QGridLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        self.setLayout(self.layout)

        # Instantiate panels
        self.selected_data_panel = SelectedDataPanel()
        self.axis_details_panel = AxisDetailsPanel()
        self.additional_text_panel = AdditionalTextPanel()
        self.custom_annotations_panel = CustomAnnotationsPanel()
        self.plot_visuals_panel = PlotVisualsPanel()
        self.plot_details_panel = PlotDetailsPanel()

        # Arrange panels in the grid layout
        self.layout.addWidget(self.selected_data_panel, 0, 0)
        self.layout.addWidget(self.axis_details_panel, 0, 1)
        self.layout.addWidget(self.plot_details_panel, 1, 0)
        self.layout.addWidget(self.plot_visuals_panel, 1, 1)
        self.layout.addWidget(self.custom_annotations_panel, 2, 0)
        self.layout.addWidget(self.additional_text_panel, 2, 1)

        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)

class NormalizationTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        self.setLayout(self.layout)

        # Placeholder content for the Normalization tab
        placeholder_label = QLabel("Normalization functionality will be implemented here.")
        placeholder_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(placeholder_label)
