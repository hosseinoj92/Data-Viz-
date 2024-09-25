# gui/main_window.py

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
    QPushButton, QShortcut, QFileDialog, QListWidgetItem, QColorDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QTabWidget, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence, QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar

from gui.tabs import GeneralTab, NormalizationTab
from plots.plotting import plot_data

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Data Viz Pro - version 2.1.1")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon('gui/resources/icon.png'))  # Set the window icon

        self.last_directory = os.path.expanduser("~")

        self.text_items = []
        self.annotations = []
        self.plot_type = "2D"
        self.text_color = 'black'
        self.annotation_mode = None  # None, 'point', 'vline', 'hline'
        self.temp_annotation = None
        self.selected_lines = []

        # Initialize central widget and layout correctly
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QGridLayout()
        self.central_widget.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # Create Tab Widget
        self.tabs = QTabWidget()
        self.general_tab = GeneralTab()
        self.normalization_tab = NormalizationTab()
        self.tabs.addTab(self.general_tab, QIcon('gui/resources/general_icon.png'), "General")
        self.tabs.addTab(self.normalization_tab, QIcon('gui/resources/normalization_icon.png'), "Normalization")

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

        self.update_button = QPushButton("Update Plot")
        # self.update_button.setIcon(QIcon('gui/resources/update_icon.png'))  # Icon removed
        self.update_button.clicked.connect(self.update_plot)

        self.show_data_structure_button = QPushButton("Show Data Structure")
        # self.show_data_structure_button.setIcon(QIcon('gui/resources/data_structure_icon.png'))  # Icon removed
        self.show_data_structure_button.clicked.connect(self.show_data_structure)

        self.plot_buttons_layout = QHBoxLayout()
        self.plot_type_2d_button = QPushButton("2D")
        # self.plot_type_2d_button.setIcon(QIcon('gui/resources/2d_icon.png'))  # Icon removed
        self.plot_type_2d_button.clicked.connect(self.plot_2d)
        self.plot_buttons_layout.addWidget(self.plot_type_2d_button)

        self.plot_type_3d_button = QPushButton("3D")
        # self.plot_type_3d_button.setIcon(QIcon('gui/resources/3d_icon.png'))  # Icon removed
        self.plot_type_3d_button.clicked.connect(self.plot_3d)
        self.plot_buttons_layout.addWidget(self.plot_type_3d_button)

        self.expand_button = QPushButton("Expand Window")
        # self.expand_button.setIcon(QIcon('gui/resources/expand_icon.png'))  # Icon removed
        self.expand_button.clicked.connect(self.expand_window)

        plot_layout.addWidget(self.update_button)
        plot_layout.addLayout(self.plot_buttons_layout)
        plot_layout.addWidget(self.show_data_structure_button)
        plot_layout.addWidget(self.expand_button)

        plot_widget = QWidget()
        plot_widget.setLayout(plot_layout)

        # Add widgets to the main layout
        self.main_layout.addWidget(self.tabs, 0, 0)
        self.main_layout.addWidget(plot_widget, 0, 1)

        self.main_layout.setColumnStretch(0, 2)
        self.main_layout.setColumnStretch(1, 3)

        # Connect signals and slots from the general tab panels
        self.connect_signals()

        # Delete shortcut
        delete_shortcut = QShortcut(QKeySequence("Delete"), self)
        delete_shortcut.activated.connect(self.delete_selected_file)

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




    def connect_signals(self):
        # Access panels from the general tab
        general_tab = self.general_tab

        self.selected_data_panel = general_tab.selected_data_panel
        self.axis_details_panel = general_tab.axis_details_panel
        self.additional_text_panel = general_tab.additional_text_panel
        self.custom_annotations_panel = general_tab.custom_annotations_panel
        self.plot_visuals_panel = general_tab.plot_visuals_panel
        self.plot_details_panel = general_tab.plot_details_panel

        # Connect signals and slots
        self.selected_data_panel.file_selector_button.clicked.connect(self.choose_files)
        self.selected_data_panel.add_file_button.clicked.connect(self.add_files)
        self.selected_data_panel.select_all_button.clicked.connect(self.toggle_select_all_files)
        self.additional_text_panel.text_color_button.clicked.connect(self.choose_text_color)
        self.additional_text_panel.add_text_button.clicked.connect(self.add_text_to_plot)
        self.additional_text_panel.delete_text_button.clicked.connect(self.delete_text_from_plot)
        self.custom_annotations_panel.apply_changes_button.clicked.connect(self.apply_changes)
        self.custom_annotations_panel.calculate_distance_button.clicked.connect(self.start_distance_calculation)

    # Include all other methods (choose_files, add_files, update_plot, etc.)
    # Ensure all methods are properly implemented as in the previous code

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

        self.canvas.draw_idle()

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
        self.data_window.setWindowTitle("Data Structure")
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
        self.data_window.setGeometry(100, 100, 800, 600)
        self.data_window.show()

    def expand_window(self):
        # Create a new window for the expanded plot
        self.expanded_window = QWidget()
        self.expanded_window.setWindowTitle("Expanded Plot")
        self.expanded_layout = QVBoxLayout(self.expanded_window)

        # Matplotlib Figure and Canvas for expanded window
        self.expanded_figure = plt.figure()
        self.expanded_canvas = FigureCanvas(self.expanded_figure)
        self.expanded_toolbar = NavigationToolbar(self.expanded_canvas, self.expanded_window)

        self.expanded_layout.addWidget(self.expanded_toolbar)
        self.expanded_layout.addWidget(self.expanded_canvas)

        self.expanded_window.setLayout(self.expanded_layout)
        self.expanded_window.setGeometry(100, 100, 1200, 800)
        self.expanded_window.show()

        self.expanded_window.closeEvent = self.close_expanded_window

        # Copy current plot to the expanded plot
        data_files = self.selected_data_panel.get_selected_files()
        plot_details = self.plot_details_panel.get_plot_details()
        axis_details = self.axis_details_panel.get_axis_details()
        plot_visuals = self.plot_visuals_panel.get_plot_visuals()

        plot_data(self.expanded_figure, data_files, plot_details, axis_details, plot_visuals, is_3d=(self.plot_type == "3D"))

    def close_expanded_window(self, event):
        self.expanded_window = None

    # Annotation functions
    def on_click(self, event):
        if self.plot_type != "2D":
            return

        annotation_type = self.custom_annotations_panel.get_annotation_type()
        if annotation_type == "Annotation Point":
            self.add_annotation_point(event)
        elif annotation_type == "Vertical Line":
            self.add_vertical_line(event)
        elif annotation_type == "Horizontal Line":
            self.add_horizontal_line(event)
        elif annotation_type == "None":
            self.select_line(event)

    def on_mouse_move(self, event):
        if self.plot_type != "2D" or not self.annotation_mode:
            return

        if self.temp_annotation:
            self.temp_annotation.remove()
            self.temp_annotation = None

        if self.annotation_mode == 'vline':
            self.temp_annotation = self.figure.gca().axvline(x=event.xdata, color='r', linestyle='--')
        elif self.annotation_mode == 'hline':
            self.temp_annotation = self.figure.gca().axhline(y=event.ydata, color='b', linestyle='--')

        self.canvas.draw_idle()

    def add_annotation_point(self, event):
        if event.xdata is None or event.ydata is None:
            return
        star, = self.figure.gca().plot(event.xdata, event.ydata, marker='*', color='black', markersize=10)
        text = self.figure.gca().text(event.xdata, event.ydata, f'({event.xdata:.2f}, {event.ydata:.2f})', fontsize=10, color='black', ha='left')
        self.annotations.append((star, text))
        self.canvas.draw_idle()

    def add_vertical_line(self, event):
        if event.xdata is None:
            return
        line = self.figure.gca().axvline(x=event.xdata, color='r', linestyle='--')
        self.annotations.append(line)
        self.canvas.draw_idle()

    def add_horizontal_line(self, event):
        if event.ydata is None:
            return
        line = self.figure.gca().axhline(y=event.ydata, color='b', linestyle='--')
        self.annotations.append(line)
        self.canvas.draw_idle()

    def apply_changes(self):
        self.annotation_mode = None
        self.temp_annotation = None
        self.custom_annotations_panel.annotation_type_combo.setCurrentText("None")
        self.canvas.draw_idle()

    def select_line(self, event):
        if event.xdata is None or event.ydata is None:
            return

        for ann in self.annotations:
            if isinstance(ann, plt.Line2D):
                # Check if it's a vertical line
                if np.allclose(ann.get_xdata(), [ann.get_xdata()[0]]) and event.inaxes == ann.axes and ann.contains(event)[0]:
                    self.selected_lines.append(ann)
                    if len(self.selected_lines) == 2:
                        self.calculate_distance()
                    break
                # Check if it's a horizontal line
                elif np.allclose(ann.get_ydata(), [ann.get_ydata()[0]]) and event.inaxes == ann.axes and ann.contains(event)[0]:
                    self.selected_lines.append(ann)
                    if len(self.selected_lines) == 2:
                        self.calculate_distance()
                    break

    def start_distance_calculation(self):
        self.selected_lines.clear()
        self.custom_annotations_panel.annotation_type_combo.setCurrentText("None")

    def calculate_distance(self):
        if len(self.selected_lines) < 2:
            return

        line1, line2 = self.selected_lines
        ax = self.figure.gca()

        if np.allclose(line1.get_xdata(), [line1.get_xdata()[0]]) and np.allclose(line2.get_xdata(), [line2.get_xdata()[0]]):  # Both lines are vertical
            x1 = line1.get_xdata()[0]
            x2 = line2.get_xdata()[0]
            dist = abs(x2 - x1)

            # Draw a horizontal arrow between the lines
            arrow = ax.annotate(f'd = {dist:.2f}', xy=((x1 + x2) / 2, ax.get_ylim()[1] - (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.05),
                                xytext=((x1 + x2) / 2, ax.get_ylim()[1] - (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.05),
                                arrowprops=dict(facecolor='black', arrowstyle='<->', lw=1.5),
                                ha='center', va='center')
            self.annotations.append(arrow)

        elif np.allclose(line1.get_ydata(), [line1.get_ydata()[0]]) and np.allclose(line2.get_ydata(), [line2.get_ydata()[0]]):  # Both lines are horizontal
            y1 = line1.get_ydata()[0]
            y2 = line2.get_ydata()[0]
            dist = abs(y2 - y1)

            # Draw a vertical arrow between the lines
            arrow = ax.annotate(f'd = {dist:.2f}', xy=(ax.get_xlim()[0] + (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.05, (y1 + y2) / 2),
                                xytext=(ax.get_xlim()[0] + (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.05, (y1 + y2) / 2),
                                arrowprops=dict(facecolor='black', arrowstyle='<->', lw=1.5),
                                ha='center', va='center', rotation=90)
            self.annotations.append(arrow)

        self.selected_lines.clear()
        self.canvas.draw_idle()
