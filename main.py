# main.py

import sys
import time
from PyQt5.QtWidgets import QApplication

from gui.main_window import MainWindow
from gui.splash_screen import SplashScreen  # Correctly import the SplashScreen

def main():
    app = QApplication(sys.argv)

    # Create and display the splash screen
    splash = SplashScreen()
    splash.show()

    # Simulate the initialization process
    for i in range(1, 101):
        splash.update_progress(i)
        time.sleep(0.02)  # Simulate some loading time

    # Create and show the main window
    window = MainWindow()
    window.show()

    # Close the splash screen
    splash.close()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
