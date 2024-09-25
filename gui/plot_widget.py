# gui/plot_widget.py

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QFrame, QShortcut
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon, QKeySequence
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar

from plots.plotting import plot_data

class ExpandedPlotWindow(QWidget):
    def __init__(self, source_figure, plot_type="2D", text_items=None, annotations=None):
        super().__init__()
        self.setWindowTitle("Expanded Plot")
        self.setGeometry(100, 100, 1200, 800)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)

        # Copy the plot from the main figure
        self.copy_plot(source_figure, plot_type, text_items, annotations)

    def copy_plot(self, source_figure, plot_type, text_items, annotations):
        self.figure.clf()
        source_axes = source_figure.get_axes()
        if not source_axes:
            return
        source_ax = source_axes[0]
        projection = '3d' if plot_type == "3D" else None
        target_ax = self.figure.add_subplot(111, projection=projection)

        # Copy lines
        for line in source_ax.get_lines():
            if plot_type == "3D" and hasattr(source_ax, 'zdata'):
                target_ax.plot(line.get_xdata(), line.get_ydata(), line.get_zdata(),
                              label=line.get_label(),
                              linestyle=line.get_linestyle(),
                              marker=line.get_marker(),
                              linewidth=line.get_linewidth())
            else:
                target_ax.plot(line.get_xdata(), line.get_ydata(),
                              label=line.get_label(),
                              linestyle=line.get_linestyle(),
                              marker=line.get_marker(),
                              linewidth=line.get_linewidth())

        # Copy annotations
        if text_items:
            for text in text_items:
                if plot_type == "3D":
                    target_ax.text(text.get_position()[0], text.get_position()[1], 0,
                                  text.get_text(),
                                  fontsize=text.get_fontsize(),
                                  color=text.get_color(),
                                  ha=text.get_ha(),
                                  va=text.get_va())
                else:
                    target_ax.text(text.get_position()[0], text.get_position()[1],
                                  text.get_text(),
                                  fontsize=text.get_fontsize(),
                                  color=text.get_color(),
                                  ha=text.get_ha(),
                                  va=text.get_va())

        # Copy lines (vertical/horizontal)
        if annotations:
            for ann in annotations:
                if isinstance(ann, plt.Line2D):
                    if np.allclose(ann.get_xdata(), [ann.get_xdata()[0]]):
                        target_ax.axvline(x=ann.get_xdata()[0], color=ann.get_color(), linestyle=ann.get_linestyle())
                    elif np.allclose(ann.get_ydata(), [ann.get_ydata()[0]]):
                        target_ax.axhline(y=ann.get_ydata()[0], color=ann.get_color(), linestyle=ann.get_linestyle())
                elif isinstance(ann, plt.Annotation):
                    target_ax.annotate(ann.get_text(),
                                       xy=ann.xy,
                                       xytext=ann.xytext,
                                       arrowprops=ann.arrowprops,
                                       ha=ann.get_ha(),
                                       va=ann.get_va(),
                                       rotation=ann.get_rotation())

        # Copy plot settings
        target_ax.set_title(source_ax.get_title(), fontsize=source_ax.get_title().get_fontsize())
        target_ax.set_xlabel(source_ax.get_xlabel(), fontsize=source_ax.get_xlabel().get_fontsize())
        target_ax.set_ylabel(source_ax.get_ylabel(), fontsize=source_ax.get_ylabel().get_fontsize())
        if plot_type == "3D":
            target_ax.set_zlabel(source_ax.get_zlabel(), fontsize=source_ax.get_zlabel().get_fontsize())

        # Copy grid
        target_ax.grid(source_ax.xaxis._gridOnMajor)

        # Copy legend
        if source_ax.get_legend():
            target_ax.legend(fontsize=source_ax.get_legend().get_fontsize())

        self.canvas.draw_idle()

class PlotWidget(QWidget):
    def __init__(self, parent=None, selected_data_panel=None, plot_details_panel=None,
                 axis_details_panel=None, plot_visuals_panel=None, additional_text_panel=None,
                 custom_annotations_panel=None):
        super().__init__(parent)

        self.selected_data_panel = selected_data_panel
        self.plot_details_panel = plot_details_panel
        self.axis_details_panel = axis_details_panel
        self.plot_visuals_panel = plot_visuals_panel
        self.additional_text_panel = additional_text_panel
        self.custom_annotations_panel = custom_annotations_panel

        self.setObjectName("PlotWidget")

        # Initialize plot attributes
        self.text_items = []
        self.annotations = []
        self.plot_type = "2D"
        self.text_color = 'black'
        self.annotation_mode = None  # None, 'point', 'vline', 'hline'
        self.temp_annotation = None
        self.selected_lines = []
        self.last_directory = os.path.expanduser("~")

        # Layouts
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Controls Layout
        self.controls_layout = QHBoxLayout()

        self.update_button = QPushButton("Update Plot")
        # self.update_button.setIcon(QIcon('gui/resources/update_icon.png'))  # Icon removed
        self.update_button.clicked.connect(self.update_plot)

        self.show_data_structure_button = QPushButton("Show Data Structure")
        # self.show_data_structure_button.setIcon(QIcon('gui/resources/data_structure_icon.png'))  # Icon removed
        self.show_data_structure_button.clicked.connect(self.show_data_structure)

        self.plot_type_2d_button = QPushButton("2D")
        # self.plot_type_2d_button.setIcon(QIcon('gui/resources/2d_icon.png'))  # Icon removed
        self.plot_type_2d_button.clicked.connect(self.plot_2d)

        self.plot_type_3d_button = QPushButton("3D")
        # self.plot_type_3d_button.setIcon(QIcon('gui/resources/3d_icon.png'))  # Icon removed
        self.plot_type_3d_button.clicked.connect(self.plot_3d)

        self.expand_button = QPushButton("Expand Window")
        # self.expand_button.setIcon(QIcon('gui/resources/expand_icon.png'))  # Icon removed
        self.expand_button.clicked.connect(self.expand_window)

        self.controls_layout.addWidget(self.update_button)
        self.controls_layout.addWidget(self.show_data_structure_button)
        self.controls_layout.addWidget(self.plot_type_2d_button)
        self.controls_layout.addWidget(self.plot_type_3d_button)
        self.controls_layout.addWidget(self.expand_button)

        self.layout.addLayout(self.controls_layout)

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

        self.layout.addWidget(self.plot_frame)

        # Connect the canvas to the event handler
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)

        # Apply stylesheet to plot_frame
        self.plot_frame.setStyleSheet("""
            #PlotFrame {
                border: 1px solid #cccccc;
                border-radius: 5px;
                background-color: #ffffff;  /* Set to white */
            }
        """)

        # Shortcuts
        self.delete_shortcut = QShortcut(QKeySequence("Delete"), self)
        self.delete_shortcut.activated.connect(self.delete_selected_file)

    def update_plot(self):
        # Gather all parameters from panels
        data_files = self.selected_data_panel.get_selected_files()
        plot_details = self.plot_details_panel.get_plot_details()
        axis_details = self.axis_details_panel.get_axis_details()
        plot_visuals = self.plot_visuals_panel.get_plot_visuals()

        # Call the plot_data function
        plot_data(
            self.figure, data_files, plot_details,
            axis_details, plot_visuals, is_3d=(self.plot_type == "3D")
        )

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
        # Get the selected file items
        selected_items = self.selected_data_panel.get_selected_file_items()
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
        self.expanded_window = ExpandedPlotWindow(
            self.figure, self.plot_type, self.text_items, self.annotations
        )
        self.expanded_window.show()

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
        text = self.figure.gca().text(
            event.xdata, event.ydata,
            f'({event.xdata:.2f}, {event.ydata:.2f})',
            fontsize=10, color='black', ha='left'
        )
        self.annotations.append((star, text))
        self.text_items.append(text)
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
            arrow = ax.annotate(
                f'd = {dist:.2f}',
                xy=((x1 + x2) / 2, ax.get_ylim()[1] - (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.05),
                xytext=((x1 + x2) / 2, ax.get_ylim()[1] - (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.05),
                arrowprops=dict(facecolor='black', arrowstyle='<->', lw=1.5),
                ha='center', va='center'
            )
            self.annotations.append(arrow)

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
            self.annotations.append(arrow)

        self.selected_lines.clear()
        self.canvas.draw_idle()

    def delete_selected_file(self):
        selected_items = self.selected_data_panel.selected_files_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.selected_data_panel.selected_files_list.takeItem(
                self.selected_data_panel.selected_files_list.row(item)
            )
