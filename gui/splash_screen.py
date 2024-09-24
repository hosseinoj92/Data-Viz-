# gui/splash_screen.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint)
        self.setFixedSize(600, 300)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Add QLabel for the image
        self.image_label = QLabel(self)
        pixmap = QPixmap("icon.png")  # Provide the path to your image here
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image_label)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setRange(0, 100)
        self.layout.addWidget(self.progress_bar)

        # Add QLabel for the main text
        self.main_text_label = QLabel("Data Viz Pro (version 1.5)", self)
        self.main_text_label.setFont(QFont("Arial", 16))
        self.main_text_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.main_text_label)

        # Add QLabel for the smaller text
        self.sub_text_label = QLabel("by Hossein Ostovar", self)
        self.sub_text_label.setFont(QFont("Arial", 10))
        self.sub_text_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.sub_text_label)

    def update_progress(self, value):
        self.progress_bar.setValue(value)
