# gui/plot_config.py

from PyQt5.QtCore import QObject, pyqtSignal

class PlotConfig(QObject):
    plot_details_changed = pyqtSignal(dict)
    axis_details_changed = pyqtSignal(dict)
    plot_visuals_changed = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.plot_details = {}
        self.axis_details = {}
        self.plot_visuals = {}

    def update_plot_details(self, new_details):
        self.plot_details = new_details
        self.plot_details_changed.emit(new_details)

    def update_axis_details(self, new_details):
        self.axis_details = new_details
        self.axis_details_changed.emit(new_details)

    def update_plot_visuals(self, new_visuals):
        self.plot_visuals = new_visuals
        self.plot_visuals_changed.emit(new_visuals)

    def get_current_config(self):
        return {
            'plot_details': self.plot_details,
            'axis_details': self.axis_details,
            'plot_visuals': self.plot_visuals,
        }
