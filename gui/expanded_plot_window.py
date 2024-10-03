# gui/expanded_plot_window.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import matplotlib.text
from PyQt5.QtCore import pyqtSignal


from plots.plotting import plot_data

# gui/expanded_plot_window.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import matplotlib.text

from plots.plotting import plot_data  # Ensure this import is correct

class ExpandedPlotWindow(QWidget):
    closed = pyqtSignal()  # Define the custom 'closed' signal

    def __init__(self, parent_tab):
        super().__init__()
        self.parent_tab = parent_tab
        self.setWindowTitle("Expanded Plot")
        self.setGeometry(150, 150, 1200, 800)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Matplotlib Figure and Canvas for expanded window
        self.expanded_figure = plt.figure()
        self.expanded_canvas = FigureCanvas(self.expanded_figure)
        self.expanded_toolbar = NavigationToolbar(self.expanded_canvas, self)

        self.layout.addWidget(self.expanded_toolbar)
        self.layout.addWidget(self.expanded_canvas)

        # Connect to parent's plot_updated signal
        self.parent_tab.plot_updated.connect(self.update_expanded_plot)

        # Initial plot
        self.update_expanded_plot()

    def update_expanded_plot(self, event=None):
        print("ExpandedPlotWindow: update_expanded_plot called")  # Debugging statement
        try:
            # Clear the expanded figure and redraw
            self.expanded_figure.clear()
            projection = '3d' if self.parent_tab.plot_type == "3D" else None
            ax = self.expanded_figure.add_subplot(111, projection=projection)

            # Re-plot using the same data and settings
            data_files = self.parent_tab.selected_data_panel.get_selected_files()
            plot_details = self.parent_tab.plot_details_panel.get_plot_details()
            axis_details = self.parent_tab.axis_details_panel.get_axis_details()
            plot_visuals = self.parent_tab.plot_visuals_panel.get_plot_visuals()
            plot_type = self.parent_tab.plot_type

            plot_data(
                self.expanded_figure, data_files, plot_details,
                axis_details, plot_visuals, is_3d=(plot_type == "3D")
            )

            # Re-add annotations
            for ann in self.parent_tab.annotations:
                if isinstance(ann, tuple):
                    # It's a (star, text) tuple
                    star, text = ann
                    ax.plot(star.get_xdata(), star.get_ydata(), marker='*', color='black', markersize=10)
                    ax.text(
                        text.get_position()[0],
                        text.get_position()[1],
                        text.get_text(),
                        fontsize=10,
                        color='black',
                        ha='left'
                    )
                elif isinstance(ann, plt.Line2D):
                    ax.add_line(ann)
                elif isinstance(ann, matplotlib.text.Annotation):
                    ax.add_artist(ann)

            # Re-add additional texts
            for text_item in self.parent_tab.text_items:
                ax.add_artist(text_item)

            self.expanded_canvas.draw_idle()
            print("ExpandedPlotWindow: update_expanded_plot completed")  # Debugging statement
        except Exception as e:
            print(f"ExpandedPlotWindow: Error in update_expanded_plot: {e}")

    def closeEvent(self, event):
        print("ExpandedPlotWindow: closeEvent called.")  # Debugging statement
        self.closed.emit()  # Emit the 'closed' signal
        super().closeEvent(event)
