"""
Entry point for Video Codec Converter (VCC).
Uses .pyw extension to suppress the console window on Windows.
"""

import sys
import os
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from vcc.ui.main_window import MainWindow


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


def main():
    # Install global exception handler to prevent silent crashes
    sys.excepthook = _global_exception_handler

    # Force the "Fusion" style so the OS native theme (dark/light) does not
    # interfere with our custom stylesheets.
    os.environ["QT_QPA_PLATFORM"] = "windows:darkmode=0"

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("Video Codec Converter")
    app.setOrganizationName("VCC")

    # Set a clean default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
