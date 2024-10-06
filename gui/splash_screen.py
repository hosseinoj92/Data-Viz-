# gui/splash_screen.py

import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("SplashScreen")

        # Remove window borders and make it transparent
        self.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Set the size of the splash screen
        self.setFixedSize(600, 400)

        # Main layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        self.setLayout(self.layout)

        # Background label
        self.background_label = QLabel(self)
        self.background_label.setGeometry(0, 0, 600, 400)
        self.background_label.setStyleSheet("background-color: rgba(43, 43, 43, 230); border-radius: 10px;")
        self.layout.addWidget(self.background_label)

        # Overlay layout to position widgets
        self.overlay_layout = QVBoxLayout(self.background_label)
        self.overlay_layout.setContentsMargins(20, 20, 20, 20)
        self.overlay_layout.setSpacing(10)
        self.overlay_layout.setAlignment(Qt.AlignCenter)

        # Logo label
        self.logo_label = QLabel(self)
        self.logo_label.setAlignment(Qt.AlignCenter)
        icon_path = self.get_resource_path('icon.png')  # Use 'icon.png' for the logo

        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            self.logo_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            print(f"Icon file not found at {icon_path}")

        self.overlay_layout.addWidget(self.logo_label)

        # Main text label
        self.main_text_label = QLabel("Data Wiz Pro", self)
        self.main_text_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.main_text_label.setStyleSheet("color: white;")
        self.main_text_label.setAlignment(Qt.AlignCenter)
        self.overlay_layout.addWidget(self.main_text_label)

        # Sub text label
        self.sub_text_label = QLabel("By Hossein Ostovar", self)
        self.sub_text_label.setFont(QFont("Segoe UI", 14))
        self.sub_text_label.setStyleSheet("color: white;")
        self.sub_text_label.setAlignment(Qt.AlignCenter)
        self.overlay_layout.addWidget(self.sub_text_label)

        # Sub text label
        self.sub_text_label = QLabel("Version 2.4.2", self)
        self.sub_text_label.setFont(QFont("Segoe UI", 12))
        self.sub_text_label.setStyleSheet("color: white;")
        self.sub_text_label.setAlignment(Qt.AlignCenter)
        self.overlay_layout.addWidget(self.sub_text_label)

        # Progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setFixedHeight(20)
        self.overlay_layout.addWidget(self.progress_bar)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def get_resource_path(self, filename):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(script_dir, 'resources', filename)
