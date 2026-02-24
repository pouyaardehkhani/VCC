"""
Entry point for Video Codec Converter (VCC).
"""

import sys
from os import sys
import os
import traceback
import platform
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QFont, QIcon
from vcc.ui.main_window import MainWindow, _detect_system_dark_mode
from vcc.ui.themes import LIGHT_THEME, DARK_THEME, get_arrow_stylesheet  # your theme module

# ------------------ Exception Handler ------------------
def _global_exception_handler(exc_type, exc_value, exc_tb):
    """Catch unhandled exceptions so the window stays open."""
    tb_text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    sys.stderr.write(tb_text)
    try:
        QMessageBox.critical(
            None,
            "Unexpected Error",
            f"An unexpected error occurred:\n\n{exc_value}\n\n"
            f"The application will continue running.\n\n"
            f"Details:\n{tb_text[-1500:]}",
        )
    except Exception:
        pass


# ------------------ Main Entry Point ------------------
def main():
    sys.excepthook = _global_exception_handler

    # Detect and set Qt platform plugin
    os_type=platform.system()
    if os_type=="Windows":
        os.environ["QT_QPA_PLATFORM"] = "windows:darkmode=0"
    elif os_type=="Linux":
        os.environ["QT_QPA_PLATFORM"] = "xcb"
    else:
        raise RuntimeError("Unsupported platform!")


    # Create QApplication
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("Video Codec Converter")
    app.setOrganizationName("VCC")

    # Set application icon
    icon_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "icon.ico")
    if not os.path.isfile(icon_path):
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
    if os.path.isfile(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Set clean default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Launch main window
    window = MainWindow()
    window.show()

    # Check and apply dark mode
    is_dark = _detect_system_dark_mode()
    window._toggle_dark_mode(is_dark)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from vcc.ui.main_window import MainWindow


def _global_exception_handler(exc_type, exc_value, exc_tb):
    """Catch unhandled exceptions so the window stays open."""
    # Format the traceback for display
    tb_text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    sys.stderr.write(tb_text)
    try:
        QMessageBox.critical(
            None,
            "Unexpected Error",
            f"An unexpected error occurred:\n\n{exc_value}\n\n"
            f"The application will continue running.\n\n"
            f"Details:\n{tb_text[-1500:]}",
        )
    except Exception:
        pass  # If even the dialog fails, at least we don't crash


def main():
    # Install global exception handler to prevent silent crashes
    sys.excepthook = _global_exception_handler

    # Force the "Fusion" style so the OS native theme (dark/light) does not
    # interfere with our custom stylesheets.
    os.environ["QT_QPA_PLATFORM"] = "windows:darkmode=0"

    # Set Windows AppUserModelID so the taskbar shows our icon
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("VCC.VideoCodecConverter.1.2")
    except Exception:
        pass

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("Video Codec Converter")
    app.setOrganizationName("VCC")

    # Set application-level icon (title bar + taskbar)
    icon_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "icon.ico")
    if not os.path.isfile(icon_path):
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
    if os.path.isfile(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Set a clean default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
