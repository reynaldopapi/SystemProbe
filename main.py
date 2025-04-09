import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication
from main_window import MainWindow
from settings_manager import SettingsManager

# Set application details for QSettings
QCoreApplication.setOrganizationName("SystemProbeOrg")
QCoreApplication.setApplicationName("SystemProbe")

def main():
    # Ensure environment variables are loaded if .env file exists
    # from dotenv import load_dotenv
    # load_dotenv() # Uncomment if using python-dotenv

    app = QApplication(sys.argv)

    settings = SettingsManager()
    main_win = MainWindow(settings)

    # Apply initial theme
    theme = settings.get_theme()
    main_win.apply_theme(theme)

    main_win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()