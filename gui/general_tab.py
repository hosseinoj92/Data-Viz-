# general_tab.py


from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QToolButton, QScrollArea, QSizePolicy,
    QPushButton, QHBoxLayout, QFrame, QFileDialog, QListWidgetItem, QColorDialog, QTableWidget, QHeaderView, QTableWidgetItem,
    QMessageBox, QButtonGroup, QGroupBox, QVBoxLayout, QDialog, QComboBox, QSpinBox, QCheckBox, QLineEdit

)
from PyQt5.QtCore import Qt, pyqtSignal, QEvent
from PyQt5.QtGui import QIcon

from gui.panels import (
    SelectedDataPanel, AxisDetailsPanel, AdditionalTextPanel,
    CustomAnnotationsPanel, PlotVisualsPanel, PlotDetailsPanel, NormalizationMethodPanel
)
from plots.plotting import plot_data
from gui.latex_compatibility_dialog import LaTeXCompatibilityDialog 

from gui.collapsible_sections import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
import matplotlib.text
from gui.expanded_plot_window import ExpandedPlotWindow 
from gui.save_plot_dialog import SavePlotDialog
import seaborn as sns
from matplotlib import style
from matplotlib import font_manager as fm
import sys
from fontTools.ttLib import TTFont

################################################################

class GeneralTab(QWidget):

    plot_updated = pyqtSignal()  # Define the custom signal

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.expanded_window = None  # To track the expanded window
        self.canvas.installEventFilter(self)


    def init_ui(self):
        self.layout = QGridLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        self.setLayout(self.layout)

        # Initialize last_directory
        self.last_directory = os.path.expanduser("~")  # Add this line

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

        # Plot area
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Create a QFrame with rounded corners for the plot
        self.plot_frame = QFrame()
        self.plot_frame.setObjectName("PlotFrame")
        self.plot_frame.setFrameShape(QFrame.StyledPanel)
        self.plot_frame.setFrameShadow(QFrame.Raised)

        # Set layout for plot_frame
        self.plot_frame_layout = QVBoxLayout(self.plot_frame)
        self.plot_frame_layout.setContentsMargins(5, 5, 5, 5)
        self.plot_frame_layout.addWidget(self.toolbar)
        self.plot_frame_layout.addWidget(self.canvas)

        # Plot area layout
        plot_layout = QVBoxLayout()
        plot_layout.addWidget(self.plot_frame)

        # Control Buttons
        self.update_button = QPushButton("Update Plot")
        self.update_button.setIcon(QIcon('gui/resources/update_icon.png'))
        self.update_button.clicked.connect(self.update_plot)

        self.show_data_structure_button = QPushButton("Show Data Structure")
        self.show_data_structure_button.setIcon(QIcon('gui/resources/data_structure_icon.png'))
        self.show_data_structure_button.clicked.connect(self.show_data_structure)

        self.plot_type_2d_button = QPushButton("2D")
        self.plot_type_2d_button.setIcon(QIcon('gui/resources/2d_icon.png'))
        self.plot_type_2d_button.clicked.connect(self.plot_2d)

        self.plot_type_3d_button = QPushButton("3D")
        self.plot_type_3d_button.setIcon(QIcon('gui/resources/3d_icon.png'))
        self.plot_type_3d_button.clicked.connect(self.plot_3d)

        self.expand_button = QPushButton("Expand Window")
        self.expand_button.setIcon(QIcon('gui/resources/expand2_icon.png'))  # Set new expand icon
        self.expand_button.clicked.connect(self.expand_window)

        self.save_plot_button = QPushButton("Save Plot")  
        self.save_plot_button.setIcon(QIcon('gui/resources/save_icon.png'))  # Optional: add an icon
        self.save_plot_button.clicked.connect(self.save_plot_with_options)

        self.configure_subplots_button = QPushButton("Configure Subplots")  
        self.configure_subplots_button.setIcon(QIcon('gui/resources/configure_subplots_icon.png')) 
        self.configure_subplots_button.clicked.connect(self.open_subplots_config_dialog)  


        self.plot_buttons_layout = QHBoxLayout()
        self.plot_buttons_layout.addWidget(self.update_button)
        self.plot_buttons_layout.addWidget(self.plot_type_2d_button)
        self.plot_buttons_layout.addWidget(self.plot_type_3d_button)
        self.plot_buttons_layout.addWidget(self.show_data_structure_button)
        self.plot_buttons_layout.addWidget(self.expand_button)
        self.plot_buttons_layout.addWidget(self.save_plot_button)
        self.plot_buttons_layout.addWidget(self.configure_subplots_button)

        plot_layout.addLayout(self.plot_buttons_layout)

        plot_widget = QWidget()
        plot_widget.setLayout(plot_layout)

        self.layout.addWidget(plot_widget, 0, 2, 3, 1)  # Span all rows in the 3rd column

        self.layout.setColumnStretch(0, 2)
        self.layout.setColumnStretch(1, 2)
        self.layout.setColumnStretch(2, 4)

        # Initialize plot type
        self.plot_type = "2D"
        self.text_items = []
        self.annotations = []
        self.annotation_mode = None  # None, 'point', 'vline', 'hline'
        self.temp_annotation = None
        self.selected_lines = []

        # Connect signals and slots from the panels
        self.connect_signals()

        # Connect the canvas to the event handler
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)



        # Update the plot_frame stylesheet
        self.plot_frame.setStyleSheet("""
            #PlotFrame {
                border: 1px solid #cccccc;
                border-radius: 5px;
                background-color: #ffffff;  /* Set to white */
            }
        """)

        configure_subplots_icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'configure_subplots_icon.png')  # New
        if os.path.exists(configure_subplots_icon_path):  # New
            self.configure_subplots_button.setIcon(QIcon(configure_subplots_icon_path))  # New
        else:  
            print(f"Warning: Configure Subplots icon not found at {configure_subplots_icon_path}")  # New
   
    def connect_signals(self):
        # Access panels
        #general_tab = self

        self.selected_data_panel.file_selector_button.clicked.connect(self.choose_files)
        self.selected_data_panel.add_file_button.clicked.connect(self.add_files)
        self.selected_data_panel.select_all_button.clicked.connect(self.toggle_select_all_files)
        self.additional_text_panel.text_color_button.clicked.connect(self.choose_text_color)
        self.additional_text_panel.add_text_button.clicked.connect(self.add_text_to_plot)
        self.additional_text_panel.delete_text_button.clicked.connect(self.delete_text_from_plot)
        self.custom_annotations_panel.apply_changes_button.clicked.connect(self.apply_changes)
        self.custom_annotations_panel.calculate_distance_button.clicked.connect(self.start_distance_calculation)

    # Include all other methods (choose_files, add_files, update_plot, etc.)
    # These methods are similar to those in the original main_window.py
    # Ensure all methods are properly implemented as in the previous code
        #self.expand_button.clicked.connect(self.expand_window)

    def choose_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", self.last_directory, "CSV Files (*.csv);;All Files (*)")
        if files:
            self.last_directory = os.path.dirname(files[0])  # Update the last directory
            self.selected_data_panel.selected_files_list.clear()
            for file in files:
                file_name = os.path.basename(file)  # Get only the file name
                item = QListWidgetItem(file_name)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                item.setData(Qt.UserRole, file)  # Store the full file path in the item
                self.selected_data_panel.selected_files_list.addItem(item)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", self.last_directory, "CSV Files (*.csv);;All Files (*)")
        if files:
            self.last_directory = os.path.dirname(files[0])  # Update the last directory
            for file in files:
                file_name = os.path.basename(file)  # Get only the file name
                item = QListWidgetItem(file_name)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                item.setData(Qt.UserRole, file)  # Store the full file path in the item
                self.selected_data_panel.selected_files_list.addItem(item)

    def toggle_select_all_files(self):
        select_all = self.selected_data_panel.select_all_button.text() == "Select All"
        for index in range(self.selected_data_panel.selected_files_list.count()):
            item = self.selected_data_panel.selected_files_list.item(index)
            item.setCheckState(Qt.Checked if select_all else Qt.Unchecked)
        self.selected_data_panel.select_all_button.setText("Deselect All" if select_all else "Select All")

    def delete_selected_file(self):
        selected_items = self.selected_data_panel.selected_files_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.selected_data_panel.selected_files_list.takeItem(self.selected_data_panel.selected_files_list.row(item))

    def choose_text_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.text_color = color.name()
            self.additional_text_panel.set_text_color(self.text_color)

    def add_text_to_plot(self):
        text_details = self.additional_text_panel.get_text_details()
        if text_details['text'] and self.plot_type == "2D":
            try:
                x_pos = float(text_details['x_pos'])
                y_pos = float(text_details['y_pos'])
                text_size = text_details['size']
                text_color = text_details['color']
                text_item = self.figure.gca().text(x_pos, y_pos, text_details['text'], fontsize=text_size, color=text_color, transform=self.figure.gca().transData, ha='left')
                self.text_items.append(text_item)
                self.canvas.draw_idle()
            except ValueError:
                print("Invalid x or y position for additional text")

    def delete_text_from_plot(self):
        if self.text_items:
            text_item = self.text_items.pop()  # Remove the last added text item
            text_item.remove()  # Remove it from the plot
            self.canvas.draw_idle()

    def update_plot(self):
        # Gather all parameters from panels
        print("GeneralTab: update_plot called")  # Debugging statement

        data_files = self.selected_data_panel.get_selected_files()
        plot_details = self.plot_details_panel.get_plot_details()
        axis_details = self.axis_details_panel.get_axis_details()
        plot_visuals = self.plot_visuals_panel.get_plot_visuals()
        # Call the plot_data function
        plot_data(self.figure, data_files, plot_details, axis_details, plot_visuals, is_3d=(self.plot_type == "3D"))

        # Re-add all existing text items
        ax = self.figure.gca()
        if self.plot_type == "2D":
            for text_item in self.text_items:
                ax.add_artist(text_item)

        # Initialize annotations list for the main axes
        if not hasattr(ax, 'annotations'):
            ax.annotations = []

        # Call the plot_data function
        plot_data(
            self.figure, data_files, plot_details,
            axis_details, plot_visuals, is_3d=(self.plot_type == "3D")
        )

        self.canvas.draw_idle()
        #print("GeneralTab: plot_updated signal emitted") 
        #self.plot_updated.emit()

    def plot_2d(self):
        self.plot_type = "2D"
        self.update_plot()

    def plot_3d(self):
        self.plot_type = "3D"
        self.update_plot()

    def show_data_structure(self):
        # Get the selected file names
        selected_items = [
            item for item in self.selected_data_panel.selected_files_list.findItems("*", Qt.MatchWildcard)
            if item.checkState() == Qt.Checked
        ]

        if not selected_items:
            return

        # Create a new window to show the data structure
        self.data_window = QWidget()
        self.data_window.setWindowTitle("Data Structure - General Tab")
        self.data_layout = QVBoxLayout(self.data_window)

        for item in selected_items:
            file_path = item.data(Qt.UserRole)
            try:
                df = pd.read_csv(file_path)
                df_head = df.head()

                table = QTableWidget()
                table.setRowCount(len(df_head))
                table.setColumnCount(len(df_head.columns))
                table.setHorizontalHeaderLabels([str(col) for col in df_head.columns])
                table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

                for i in range(len(df_head)):
                    for j in range(len(df_head.columns)):
                        table.setItem(i, j, QTableWidgetItem(str(df_head.iloc[i, j])))

                self.data_layout.addWidget(QLabel(item.text()))
                self.data_layout.addWidget(table)
            except Exception as e:
                print(f"Error loading file {file_path}: {e}")

        self.data_window.setLayout(self.data_layout)
        self.data_window.setGeometry(150, 150, 800, 600)
        self.data_window.show()

    def eventFilter(self, obj, event):
        if obj == self.canvas and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape:
                self.custom_annotations_panel.apply_changes_button.click()
                return True  # Event handled
        return super(GeneralTab, self).eventFilter(obj, event)


    def expand_window(self):
        print("Expand Window button clicked.")

        if self.expanded_window is not None:
            print("Expanded window already exists, bringing it to front.")
            self.expanded_window.raise_()
            return

        # Create a new window for the expanded plot
        try:
            print("GeneralTab: Creating a new ExpandedPlotWindow.")
            self.expanded_window = ExpandedPlotWindow(self)
            self.expanded_window.closed.connect(self.on_expanded_window_closed)
            self.expanded_window.show()
        except Exception as e:
            print(f"GeneralTab: Error creating ExpandedPlotWindow: {e}")

        # Connect to the closed signal to reset the reference
        #self.expanded_window.destroyed.connect(self.on_expanded_window_closed)

    def on_expanded_window_closed(self):
            print("Expanded window closed.")
            self.expanded_window = None  # Reset the reference when the window is closed
            print("self.expanded_window has been reset to None.")
        
    def on_click(self, event):
        if event.inaxes is None:
            return

        ax = event.inaxes

        # Get annotation type from the main CustomAnnotationsPanel
        annotation_type = self.custom_annotations_panel.get_annotation_type()

        # Apply annotations to this axes (subplot or main plot)
        self.apply_annotation(ax, event, annotation_type)




    def on_mouse_move(self, event):
        if event.inaxes is None:
            return

        ax = event.inaxes

        # Get annotation type from the main CustomAnnotationsPanel
        annotation_type = self.custom_annotations_panel.get_annotation_type()

        if annotation_type not in ['Vertical Line', 'Horizontal Line']:
            return

        if self.temp_annotation:
            self.temp_annotation.remove()
            self.temp_annotation = None

        if annotation_type == 'Vertical Line':
            if event.xdata is not None:
                self.temp_annotation = ax.axvline(x=event.xdata, color='r', linestyle='--')
        elif annotation_type == 'Horizontal Line':
            if event.ydata is not None:
                self.temp_annotation = ax.axhline(y=event.ydata, color='b', linestyle='--')

        self.canvas.draw_idle()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.custom_annotations_panel.apply_changes_button.click()
            event.accept()
        else:
            super().keyPressEvent(event)


    def apply_annotation(self, ax, event, annotation_type):
        if annotation_type == "Annotation Point":
            self.add_annotation_point(ax, event)
        elif annotation_type == "Vertical Line":
            self.add_vertical_line(ax, event)
        elif annotation_type == "Horizontal Line":
            self.add_horizontal_line(ax, event)
        elif annotation_type == "None":
            self.select_line(ax, event)

    def add_annotation_point(self, ax, event):
        if event.xdata is None or event.ydata is None:
            return
        star, = ax.plot(event.xdata, event.ydata, marker='*', color='black', markersize=10)
        text = ax.text(event.xdata, event.ydata, f'({event.xdata:.2f}, {event.ydata:.2f})', fontsize=10, color='black', ha='left')
        # Store annotations per axes
        if not hasattr(ax, 'annotations'):
            ax.annotations = []
        ax.annotations.append((star, text))
        self.canvas.draw_idle()



    def add_vertical_line(self, ax, event):
        if event.xdata is None:
            return
        line = ax.axvline(x=event.xdata, color='r', linestyle='--')
        if not hasattr(ax, 'annotations'):
            ax.annotations = []
        ax.annotations.append(line)
        self.canvas.draw_idle()


    def add_horizontal_line(self, ax, event):
        if event.ydata is None:
            return
        line = ax.axhline(y=event.ydata, color='b', linestyle='--')
        if not hasattr(ax, 'annotations'):
            ax.annotations = []
        ax.annotations.append(line)
        self.canvas.draw_idle()



    def apply_changes(self):
        self.annotation_mode = None
        self.temp_annotation = None
        # Reset annotation type in the main CustomAnnotationsPanel
        self.custom_annotations_panel.annotation_type_combo.setCurrentText("None")
        self.canvas.draw_idle()


    def select_line(self, ax, event):
        if event.xdata is None or event.ydata is None:
            return

        for ann in getattr(ax, 'annotations', []):
            if isinstance(ann, plt.Line2D):
                # Check if it's a vertical line
                if np.allclose(ann.get_xdata(), [ann.get_xdata()[0]]) and ann.contains(event)[0]:
                    self.selected_lines.append(ann)
                    if len(self.selected_lines) == 2:
                        self.calculate_distance(ax)
                    break
                # Check if it's a horizontal line
                elif np.allclose(ann.get_ydata(), [ann.get_ydata()[0]]) and ann.contains(event)[0]:
                    self.selected_lines.append(ann)
                    if len(self.selected_lines) == 2:
                        self.calculate_distance(ax)
                    break

    def start_distance_calculation(self):
        self.selected_lines.clear()
        # Reset annotation type in the main CustomAnnotationsPanel
        self.custom_annotations_panel.annotation_type_combo.setCurrentText("None")

    def calculate_distance(self, ax):
        if len(self.selected_lines) < 2:
            return

        line1, line2 = self.selected_lines

        if np.allclose(line1.get_xdata(), [line1.get_xdata()[0]]) and np.allclose(line2.get_xdata(), [line2.get_xdata()[0]]):  # Both lines are vertical
            x1 = line1.get_xdata()[0]
            x2 = line2.get_xdata()[0]
            dist = abs(x2 - x1)

            # Draw a horizontal arrow between the lines
            arrow = ax.annotate(
                f'd = {dist:.2f}',
                xy=((x1 + x2) / 2, ax.get_ylim()[1] - (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.05),
                xytext=((x1 + x2) / 2, ax.get_ylim()[1] - (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.05),
                arrowprops=dict(facecolor='black', arrowstyle='<->', lw=1.5),
                ha='center', va='center'
            )
            ax.annotations.append(arrow)

        elif np.allclose(line1.get_ydata(), [line1.get_ydata()[0]]) and np.allclose(line2.get_ydata(), [line2.get_ydata()[0]]):  # Both lines are horizontal
            y1 = line1.get_ydata()[0]
            y2 = line2.get_ydata()[0]
            dist = abs(y2 - y1)

            # Draw a vertical arrow between the lines
            arrow = ax.annotate(
                f'd = {dist:.2f}',
                xy=(ax.get_xlim()[0] + (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.05, (y1 + y2) / 2),
                xytext=(ax.get_xlim()[0] + (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.05, (y1 + y2) / 2),
                arrowprops=dict(facecolor='black', arrowstyle='<->', lw=1.5),
                ha='center', va='center', rotation=90
            )
            ax.annotations.append(arrow)

        self.selected_lines.clear()
        self.canvas.draw_idle()

    def apply_style_to_axes(self, ax, style_dict):
    # Apply style parameters to the axes
        for key, value in style_dict.items():
            if key.startswith('axes.'):
                param_name = key[5:]  # Remove 'axes.' prefix
                if param_name == 'facecolor':
                    ax.set_facecolor(value)
                elif param_name == 'edgecolor':
                    for spine in ax.spines.values():
                        spine.set_edgecolor(value)
                elif param_name == 'labelcolor':
                    ax.xaxis.label.set_color(value)
                    ax.yaxis.label.set_color(value)
                elif param_name == 'titlesize':
                    ax.title.set_fontsize(value)
                elif param_name == 'titleweight':
                    ax.title.set_fontweight(value)
                # Add more axes-related styles as needed
            elif key.startswith('xtick.'):
                param_name = key[6:]  # Remove 'xtick.' prefix
                if param_name == 'color':
                    ax.tick_params(axis='x', colors=value)
                elif param_name == 'labelsize':
                    ax.tick_params(axis='x', labelsize=value)
                # Add more xtick-related styles as needed
            elif key.startswith('ytick.'):
                param_name = key[6:]  # Remove 'ytick.' prefix
                if param_name == 'color':
                    ax.tick_params(axis='y', colors=value)
                elif param_name == 'labelsize':
                    ax.tick_params(axis='y', labelsize=value)
                # Add more ytick-related styles as needed
            elif key == 'grid.color':
                ax.grid(True, color=value)
            elif key == 'grid.linestyle':
                ax.grid(True, linestyle=value)
            elif key == 'grid.linewidth':
                ax.grid(True, linewidth=value)
            elif key == 'lines.linewidth':
                pass  # Handled in plot function
            elif key == 'lines.linestyle':
                pass  # Handled in plot function
            elif key == 'text.color':
                ax.title.set_color(value)
                ax.xaxis.label.set_color(value)
                ax.yaxis.label.set_color(value)
                for text in ax.texts:
                    text.set_color(value)
            # Handle other style parameters as needed


    def apply_font_settings(self, font_family, title_font_size, axis_font_size):
        for ax in self.figure.axes:
            # Update titles
            ax.title.set_fontsize(title_font_size)
            ax.title.set_fontfamily(font_family)

            # Update axis labels
            ax.xaxis.label.set_fontsize(axis_font_size)
            ax.xaxis.label.set_fontfamily(font_family)
            ax.yaxis.label.set_fontsize(axis_font_size)
            ax.yaxis.label.set_fontfamily(font_family)

            # Update tick labels
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontsize(axis_font_size)
                label.set_fontfamily(font_family)

            # Update legend
            legend = ax.get_legend()
            if legend:
                for text in legend.get_texts():
                    text.set_fontsize(axis_font_size)
                    text.set_fontfamily(font_family)

            # Update annotations
            for child in ax.get_children():
                if isinstance(child, matplotlib.text.Annotation):
                    child.set_fontsize(axis_font_size)
                    child.set_fontfamily(font_family)

    def save_plot_with_options(self):
        print("Save Plot button clicked.")
        dialog = SavePlotDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            width_pixels, height_pixels, quality, latex_options = dialog.get_values()
            print(f"Saving plot with width: {width_pixels}px, height: {height_pixels}px, quality: {quality}")
            self.save_plot(width_pixels, height_pixels, quality, latex_options)

    def save_plot(self, width_pixels, height_pixels, quality, latex_options):
        # Map quality to dpi
        quality_dpi_mapping = {
            "Low": 72,
            "Medium": 150,
            "High": 300,
            "Very High": 600
        }
        dpi = quality_dpi_mapping.get(quality, 150)  # Default to 150 DPI if not found

        # Convert pixels to inches (assuming 100 pixels = 1 inch for simplicity)
        width_in = width_pixels / 100
        height_in = height_pixels / 100

        # Store original figure size, DPI, and rcParams
        original_size = self.figure.get_size_inches()
        original_dpi = self.figure.get_dpi()
        original_rcparams = plt.rcParams.copy()

        try:
            # Apply LaTeX settings if provided
            if latex_options:
                selected_font = latex_options['font_family']
                print(f"Selected font: '{selected_font}'")

                # Set figure size based on LaTeX settings
                width_unit = latex_options['width_unit']
                figure_width = latex_options['figure_width']
                if width_unit == 'inches':
                    width_in_inches = figure_width
                elif width_unit == 'cm':
                    width_in_inches = figure_width / 2.54
                elif width_unit == 'mm':
                    width_in_inches = figure_width / 25.4
                elif width_unit == 'pt':
                    width_in_inches = figure_width / 72.27
                elif width_unit == 'textwidth fraction':
                    # Assume standard LaTeX textwidth is 6.5 inches
                    width_in_inches = figure_width * 6.5
                else:
                    width_in_inches = figure_width  # Default to inches

                # Set figure size and DPI
                self.figure.set_size_inches(width_in_inches, self.figure.get_size_inches()[1])
                self.figure.set_dpi(latex_options['dpi'])

                # Update rcParams for font settings
                plt.rcParams.update({
                    'font.size': latex_options['base_font_size'],
                    'font.family': selected_font,
                })

                if latex_options['use_latex']:
                    plt.rcParams.update({
                        'text.usetex': True,
                        'font.family': selected_font,
                    })
                else:
                    plt.rcParams.update({'text.usetex': False})

                # Apply font settings to plot titles and axis labels
                self.apply_font_settings(
                    selected_font,
                    latex_options['title_font_size'],
                    latex_options['axis_font_size']
                )
            else:
                # If no LaTeX settings, apply the user-specified image size and quality
                self.figure.set_size_inches(width_in, height_in)
                self.figure.set_dpi(dpi)

            # Define the file path
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Save Plot", 
                "", 
                "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)", 
                options=options
            )
            if file_path:
                try:
                    # Save the figure with the specified DPI
                    self.figure.savefig(file_path, dpi=dpi)
                    QMessageBox.information(self, "Save Successful", f"Plot saved successfully at:\n{file_path}")
                    print(f"Plot saved successfully at: {file_path}")
                except Exception as e:
                    QMessageBox.warning(self, "Save Failed", f"Failed to save plot:\n{e}")
                    print(f"Failed to save plot: {e}")

        finally:
            # Restore original figure size, DPI, and rcParams to keep the interactive plot unaffected
            self.figure.set_size_inches(original_size)
            self.figure.set_dpi(original_dpi)
            plt.rcParams.update(original_rcparams)

            # Redraw the canvas to reflect original settings
            self.canvas.draw_idle()
            print("Figure size, DPI, and rcParams restored to original after saving.")

        
    def open_subplots_config_dialog(self):
        dialog = SubplotsConfigDialog(self)  # Pass self (GeneralTab) as parent
        if dialog.exec_() == QDialog.Accepted:
            self.subplot_widgets = dialog.subplot_configs  # Keep the widgets
            self.subplot_configs_data = dialog.get_subplot_configs()  # Get the configs (dicts)
            self.layout_settings = dialog.get_layout_settings()
            self.update_plot_with_subplots()

    def update_plot_with_subplots(self):

        # Store current rcParams
        original_rcparams = plt.rcParams.copy()

        if not hasattr(self, 'subplot_configs_data') or not self.subplot_configs_data:
            self.update_plot()  # Use existing plotting if no subplots are configured
            return

        # Clear the existing figure
        self.figure.clear()

        # Determine the layout based on user settings
        if self.layout_settings.get('auto_layout', False):
            num_subplots = len(self.subplot_configs_data)
            cols = int(np.ceil(np.sqrt(num_subplots)))
            rows = int(np.ceil(num_subplots / cols))
        else:
            rows = self.layout_settings.get('rows', 1)
            cols = self.layout_settings.get('columns', 1)

        # Set figure size based on the number of rows and columns
        self.figure.set_size_inches(5 * cols, 4 * rows)

        # Create subplots
        try:
            axes = self.figure.subplots(rows, cols, squeeze=False)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to create subplots: {e}")
            return

        # Flatten the axes array for easy iteration
        axes = axes.flatten()

        # Iterate through each subplot configuration
        for idx, config in enumerate(self.subplot_configs_data):
            if idx >= len(axes):
                break  # Prevent index out of range if more subplots are configured than available axes

            ax = axes[idx]
            try:
                # Extract advanced options
                advanced_options = config.get('advanced_options', {})
                line_style = {
                    'Solid': '-',
                    'Dashed': '--',
                    'Dash-Dot': '-.'
                }.get(advanced_options.get('line_style', 'Solid'), '-')
                point_style = {
                    'None': '',
                    'Circle': 'o',
                    'Square': 's',
                    'Triangle Up': '^',
                    'Triangle Down': 'v',
                    'Star': '*',
                    'Plus': '+',
                    'Cross': 'x'
                }.get(advanced_options.get('point_style', 'None'), '')
                line_thickness = int(advanced_options.get('line_thickness', 2))
                scale_type = advanced_options.get('scale_type', 'Linear')
                plot_style = advanced_options.get('plot_style', 'default')

                # Retrieve the style dictionary
                style_dict = plt.style.library.get(plot_style, {})

                # Apply style parameters to the axes
                self.apply_style_to_axes(ax, style_dict)

                 # Apply LaTeX options if they exist
                latex_options = config.get('latex_options', None)
                if latex_options:
                    self.apply_latex_compatibility_to_axes(ax, latex_options)  

                # Plot datasets
                for dataset_config in config['datasets']:
                    df = pd.read_csv(dataset_config['dataset'])
                    x = df.iloc[:, int(dataset_config['x_column'])]
                    y = df.iloc[:, int(dataset_config['y_column'])]
                    label = dataset_config['legend_label']
                    ax.plot(
                        x, y, label=rf"{label}",
                        linestyle=line_style,
                        marker=point_style if point_style != '' else None,
                        linewidth=line_thickness
                    )

                # Set axis labels with LaTeX rendering
                ax.set_xlabel(rf"{config.get('x_axis_label', '')}", fontsize=12)
                ax.set_ylabel(rf"{config.get('y_axis_label', '')}", fontsize=12)

                # Set subplot title with customizable font size and LaTeX
                ax.set_title(rf"{config.get('subplot_title', f'Subplot {idx + 1}')}", fontsize=config.get('title_font_size', 14))

                # Set scale type
                x_scale = 'linear'
                y_scale = 'linear'
                if scale_type == 'Logarithmic X-Axis':
                    x_scale = 'log'
                elif scale_type == 'Logarithmic Y-Axis':
                    y_scale = 'log'
                elif scale_type == 'Logarithmic Both Axes':
                    x_scale = 'log'
                    y_scale = 'log'
                ax.set_xscale(x_scale)
                ax.set_yscale(y_scale)

                # Enable legend if required with customizable font size
                if config.get('enable_legend'):
                    legend_location = config.get('legend_location', 'best')
                    ax.legend(loc=legend_location, fontsize=config.get('legend_font_size', 10))
                else:
                    print(f"Legend not enabled for Subplot {idx + 1}")

                # Enable grid if required
                if config.get('enable_grid'):
                    print(f"Enabling grid for Subplot {idx + 1}")
                    ax.minorticks_on()
                    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
                    # Optional: Customize minor tick appearance
                    ax.tick_params(which='minor', length=4, color='gray')
                else:
                    print(f"Grid not enabled for Subplot {idx + 1}")

                # Initialize annotations list for this subplot
                if not hasattr(ax, 'annotations'):
                    ax.annotations = []

                # Store the subplot index in the axes object for event handling (optional)
                ax.subplot_index = idx

            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to plot Subplot {idx + 1}: {e}")
            # **Restore original rcParams if needed**
        plt.rcParams.update(original_rcparams)

        # Hide any unused axes
        for idx in range(len(self.subplot_configs_data), len(axes)):
            self.figure.delaxes(axes[idx])

        # Adjust layout for better spacing
        try:
            self.figure.tight_layout()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to adjust layout: {e}")

        # Render the updated plot
        self.canvas.draw_idle()
