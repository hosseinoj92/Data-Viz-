# main.py

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

from gui.main_window import MainWindow
from gui.splash_screen import SplashScreen

def main():
    app = QApplication(sys.argv)

    # Load and apply the stylesheet
    try:
        with open('style.qss', 'r') as f:
            stylesheet = f.read()
            app.setStyleSheet(stylesheet)
    except Exception as e:
        print(f"Error loading stylesheet: {e}")

    # Create and display the splash screen
    splash = SplashScreen()
    splash.show()

    # Initialize the main window variable
    window = None

    def show_main_window():
        nonlocal window
        window = MainWindow()
        window.show()
        # Close the splash screen after the main window is shown
        splash.close()  # Use close() instead of finish()

    # Simulate the initialization process with timers
    progress = 0

    def update_progress():
        nonlocal progress
        progress += 5  # Increment progress
        splash.update_progress(progress)
        if progress >= 100:
            progress_timer.stop()
            # Show the main window
            show_main_window()

    progress_timer = QTimer()
    progress_timer.timeout.connect(update_progress)
    progress_timer.start(100)  # Update progress every 100 ms

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
