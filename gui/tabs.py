# gui/tabs.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QToolButton, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt
from gui.panels import (
    SelectedDataPanel, AxisDetailsPanel, AdditionalTextPanel,
    CustomAnnotationsPanel, PlotVisualsPanel, PlotDetailsPanel
)
from PyQt5.QtGui import QIcon


class CollapsibleSection(QWidget):
    def __init__(self, title, content_widget, parent=None):
        super().__init__(parent)
        self.toggle_button = QToolButton(text=title, checkable=True, checked=False)
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.RightArrow)
        self.toggle_button.clicked.connect(self.on_toggle)

        self.content_area = QWidget()
        self.content_area.setMaximumHeight(0)
        self.content_area.setMinimumHeight(0)

        self.toggle_animation = None  # Placeholder for animation if needed

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content_area)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        self.setLayout(main_layout)

        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(15, 0, 0, 0)
        self.content_layout.setSpacing(5)
        self.content_area.setLayout(self.content_layout)
        self.content_layout.addWidget(content_widget)

    def on_toggle(self):
        if self.toggle_button.isChecked():
            self.toggle_button.setArrowType(Qt.DownArrow)
            self.content_area.setMaximumHeight(16777215)  # Expand to full size
        else:
            self.toggle_button.setArrowType(Qt.RightArrow)
            self.content_area.setMaximumHeight(0)  # Collapse


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
        # Main layout for the Normalization Tab
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(5)
        self.setLayout(self.layout)

        # Selected Data Panel
        self.selected_data_panel = SelectedDataPanel()

        # Create collapsible sections for other panels
        self.collapsible_sections = []

        # Plot Details Section
        self.plot_details_panel = PlotDetailsPanel()
        plot_details_section = CollapsibleSection("Plot Details", self.plot_details_panel)
        self.collapsible_sections.append(plot_details_section)

        # Axis Details Section
        self.axis_details_panel = AxisDetailsPanel()
        axis_details_section = CollapsibleSection("Axis Details", self.axis_details_panel)
        self.collapsible_sections.append(axis_details_section)

        # Plot Visuals Section
        self.plot_visuals_panel = PlotVisualsPanel()
        plot_visuals_section = CollapsibleSection("Plot Visuals", self.plot_visuals_panel)
        self.collapsible_sections.append(plot_visuals_section)

        # Custom Annotations Section
        self.custom_annotations_panel = CustomAnnotationsPanel()
        custom_annotations_section = CollapsibleSection("Custom Annotations", self.custom_annotations_panel)
        self.collapsible_sections.append(custom_annotations_section)

        # Additional Text Section
        self.additional_text_panel = AdditionalTextPanel()
        additional_text_section = CollapsibleSection("Additional Text", self.additional_text_panel)
        self.collapsible_sections.append(additional_text_section)

        # Add Selected Data Panel to the layout
        self.layout.addWidget(self.selected_data_panel)

        # Add collapsible sections beneath Selected Data
        for section in self.collapsible_sections:
            self.layout.addWidget(section)

        # Spacer to push content to the top
        self.layout.addStretch()

    def add_general_data(self, data_items):
        """
        Adds data items from the GeneralTab to the NormalizationTab's Selected Data Panel.
        """
        for item in data_items:
            self.selected_data_panel.add_item(item)

    def get_selected_files(self):
        """
        Returns the list of selected files in the NormalizationTab.
        """
        return self.selected_data_panel.get_selected_files()
