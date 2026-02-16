"""
Theme definitions for VCC - Light and Dark mode stylesheets.
"""

import os
import tempfile

_arrow_cache: dict[str, str] = {}


def _ensure_arrow_images() -> dict[str, str]:
    """Create small arrow PNG images for use in stylesheets.

    Must be called after QApplication exists (QPixmap requires it).
    Returns a dict mapping arrow names to file paths (forward-slash).
    """
    if _arrow_cache:
        return _arrow_cache

    from PyQt6.QtGui import QPixmap, QPainter, QColor, QPolygon
    from PyQt6.QtCore import QPoint, Qt

    arrow_dir = tempfile.mkdtemp(prefix="vcc_arrows_")

    configs = {
        "dark_down":  ("#333333", "down"),   # dark arrow → light theme
        "dark_up":    ("#333333", "up"),
        "light_down": ("#e0e0e0", "down"),   # light arrow → dark theme
        "light_up":   ("#e0e0e0", "up"),
    }

    for name, (color, direction) in configs.items():
        sz = 10
        pixmap = QPixmap(sz, sz)
        pixmap.fill(QColor(0, 0, 0, 0))  # transparent
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(color))
        painter.setPen(Qt.PenStyle.NoPen)

        if direction == "down":
            points = [QPoint(1, 3), QPoint(sz - 1, 3), QPoint(sz // 2, sz - 2)]
        else:
            points = [QPoint(1, sz - 3), QPoint(sz - 1, sz - 3), QPoint(sz // 2, 2)]

        painter.drawPolygon(QPolygon(points))
        painter.end()

        path = os.path.join(arrow_dir, f"{name}.png")
        pixmap.save(path, "PNG")
        _arrow_cache[name] = path.replace("\\", "/")

    return _arrow_cache


def get_arrow_stylesheet(dark: bool) -> str:
    """Return a stylesheet fragment that sets arrow images for
    QComboBox and QSpinBox / QDoubleSpinBox.

    Call *after* QApplication has been created.
    """
    paths = _ensure_arrow_images()

    if dark:
        down = paths["light_down"]
        up   = paths["light_up"]
    else:
        down = paths["dark_down"]
        up   = paths["dark_up"]

    return f"""
    QComboBox::down-arrow {{
        image: url({down});
        width: 10px;
        height: 10px;
    }}
    QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
        image: url({up});
        width: 10px;
        height: 10px;
    }}
    QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
        image: url({down});
        width: 10px;
        height: 10px;
    }}
    """

LIGHT_THEME = """
    QWidget {
        font-family: 'Segoe UI', sans-serif;
        color: #222;
    }
    QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit {
        padding: 4px 6px;
        border: 1px solid #c0c0c0;
        border-radius: 4px;
        background: #fff;
        color: #222;
    }
    QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QLineEdit:focus {
        border-color: #4a90d9;
    }
    QPushButton {
        padding: 5px 14px;
        border: 1px solid #bbb;
        border-radius: 4px;
        background: #f5f5f5;
        color: #222;
    }
    QPushButton:hover {
        background: #e8e8e8;
        border-color: #999;
    }
    QPushButton:pressed {
        background: #ddd;
    }
    QCheckBox {
        spacing: 6px;
        color: #222;
    }
    QLabel {
        color: #222;
    }
    QGroupBox {
        color: #333;
    }
    QListWidget {
        background: #fff;
        color: #222;
        border: 1px solid #c0c0c0;
    }
    QListWidget::item:selected {
        background: #cde4ff;
        color: #222;
    }
    QScrollArea {
        background: transparent;
    }
    QComboBox QAbstractItemView {
        background: #fff;
        color: #222;
        selection-background-color: #cde4ff;
        selection-color: #222;
    }
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: center right;
        width: 18px;
        border-left: 1px solid #c0c0c0;
        background: #f0f0f0;
    }
    QComboBox::drop-down:hover {
        background: #e0e0e0;
    }
    QSpinBox::up-button, QDoubleSpinBox::up-button {
        subcontrol-origin: border;
        subcontrol-position: top right;
        width: 18px;
        border-left: 1px solid #c0c0c0;
        background: #f0f0f0;
    }
    QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {
        background: #e0e0e0;
    }
    QSpinBox::down-button, QDoubleSpinBox::down-button {
        subcontrol-origin: border;
        subcontrol-position: bottom right;
        width: 18px;
        border-left: 1px solid #c0c0c0;
        background: #f0f0f0;
    }
    QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
        background: #e0e0e0;
    }
    QTextBrowser {
        background-color: #FFFFFF;  /* white background */
        color: #333333;             /* dark gray text */
        border: 1px solid #CCCCCC;  /* light gray border */
        border-radius: 4px;
        padding: 8px;
    }
"""

DARK_THEME = """
    QWidget {
        font-family: 'Segoe UI', sans-serif;
        background-color: #2b2b2b;
        color: #e0e0e0;
    }
    QMainWindow {
        background-color: #2b2b2b;
    }
    QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit {
        padding: 4px 6px;
        border: 1px solid #555;
        border-radius: 4px;
        background: #3c3c3c;
        color: #e0e0e0;
    }
    QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QLineEdit:focus {
        border-color: #5a9fd4;
    }
    QSpinBox::up-button, QSpinBox::down-button,
    QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
        background: #4a4a4a;
        border: 1px solid #555;
        width: 18px;
    }
    QSpinBox::up-button:hover, QSpinBox::down-button:hover,
    QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
        background: #5a5a5a;
    }
    QSpinBox::up-button, QDoubleSpinBox::up-button {
        subcontrol-origin: border;
        subcontrol-position: top right;
    }
    QSpinBox::down-button, QDoubleSpinBox::down-button {
        subcontrol-origin: border;
        subcontrol-position: bottom right;
    }
    QPushButton {
        padding: 5px 14px;
        border: 1px solid #555;
        border-radius: 4px;
        background: #3c3c3c;
        color: #e0e0e0;
    }
    QPushButton:hover {
        background: #4a4a4a;
        border-color: #666;
    }
    QPushButton:pressed {
        background: #505050;
    }
    QCheckBox {
        spacing: 6px;
        color: #e0e0e0;
    }
    QCheckBox::indicator {
        width: 16px;
        height: 16px;
        border: 1px solid #666;
        border-radius: 3px;
        background: #3c3c3c;
    }
    QCheckBox::indicator:checked {
        background: #5a9fd4;
        border-color: #5a9fd4;
    }
    QLabel {
        color: #e0e0e0;
        background: transparent;
    }
    QGroupBox {
        font-weight: bold;
        font-size: 12px;
        border: 1px solid #555;
        border-radius: 6px;
        margin-top: 10px;
        padding-top: 14px;
        background-color: #333;
        color: #e0e0e0;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 6px;
        color: #ccc;
    }
    QListWidget {
        background: #333;
        color: #e0e0e0;
        border: 1px solid #555;
        border-radius: 4px;
        font-size: 11px;
    }
    QListWidget::item {
        padding: 2px 4px;
    }
    QListWidget::item:selected {
        background: #3a5a8a;
        color: #fff;
    }
    QScrollArea {
        background: transparent;
        border: none;
    }
    QScrollBar:vertical {
        background: #2b2b2b;
        width: 12px;
        border: none;
    }
    QScrollBar::handle:vertical {
        background: #555;
        min-height: 20px;
        border-radius: 4px;
        margin: 2px;
    }
    QScrollBar::handle:vertical:hover {
        background: #666;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
    }
    QScrollBar:horizontal {
        background: #2b2b2b;
        height: 12px;
        border: none;
    }
    QScrollBar::handle:horizontal {
        background: #555;
        min-width: 20px;
        border-radius: 4px;
        margin: 2px;
    }
    QScrollBar::handle:horizontal:hover {
        background: #666;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0;
    }
    QComboBox QAbstractItemView {
        background: #3c3c3c;
        color: #e0e0e0;
        selection-background-color: #3a5a8a;
        selection-color: #fff;
        border: 1px solid #555;
    }
    QComboBox::drop-down {
        border-left: 1px solid #555;
        background: #4a4a4a;
        subcontrol-origin: padding;
        subcontrol-position: center right;
        width: 18px;
    }
    QComboBox::drop-down:hover {
        background: #5a5a5a;
    }
    QMenuBar {
        background: #333;
        border-bottom: 1px solid #555;
        padding: 2px 0;
        color: #e0e0e0;
    }
    QMenuBar::item {
        padding: 4px 12px;
        border-radius: 4px;
        color: #e0e0e0;
    }
    QMenuBar::item:selected {
        background: #3a5a8a;
    }
    QMenu {
        background: #3c3c3c;
        border: 1px solid #555;
        padding: 4px 0;
        color: #e0e0e0;
    }
    QMenu::item {
        padding: 6px 30px 6px 20px;
        color: #e0e0e0;
    }
    QMenu::item:selected {
        background: #3a5a8a;
    }
    QMenu::separator {
        height: 1px;
        background: #555;
        margin: 4px 10px;
    }
    QProgressBar {
        border: 1px solid #555;
        border-radius: 4px;
        text-align: center;
        height: 22px;
        background: #3c3c3c;
        color: #e0e0e0;
    }
    QProgressBar::chunk {
        background-color: #4caf50;
        border-radius: 3px;
    }
    QStatusBar {
        border-top: 1px solid #555;
        color: #aaa;
        background: #2b2b2b;
    }
    QToolTip {
        background-color: #3c3c3c;
        color: #e0e0e0;
        border: 1px solid #555;
        padding: 6px;
        font-size: 12px;
    }
    QTextBrowser {
        background-color: #5C5C5C;
        color: #e0e0e0;
        border: 1px solid #555;
        border-radius: 4px;
        padding: 8px;
    }
    QDialog {
        background-color: #2b2b2b;
        color: #e0e0e0;
    }
"""

LIGHT_MENUBAR_STYLE = """
    QMenuBar {
        background: #f5f5f5;
        border-bottom: 1px solid #d0d0d0;
        padding: 2px 0;
    }
    QMenuBar::item {
        padding: 4px 12px;
        border-radius: 4px;
    }
    QMenuBar::item:selected {
        background: #dce9f9;
    }
    QMenu {
        background: #ffffff;
        border: 1px solid #c0c0c0;
        padding: 4px 0;
    }
    QMenu::item {
        padding: 6px 30px 6px 20px;
    }
    QMenu::item:selected {
        background: #dce9f9;
    }
"""

DARK_MENUBAR_STYLE = """
    QMenuBar {
        background: #333;
        border-bottom: 1px solid #555;
        padding: 2px 0;
        color: #e0e0e0;
    }
    QMenuBar::item {
        padding: 4px 12px;
        border-radius: 4px;
        color: #e0e0e0;
    }
    QMenuBar::item:selected {
        background: #3a5a8a;
    }
    QMenu {
        background: #3c3c3c;
        border: 1px solid #555;
        padding: 4px 0;
        color: #e0e0e0;
    }
    QMenu::item {
        padding: 6px 30px 6px 20px;
        color: #e0e0e0;
    }
    QMenu::item:selected {
        background: #3a5a8a;
    }
    QMenu::separator {
        height: 1px;
        background: #555;
        margin: 4px 10px;
    }
"""

LIGHT_GROUP_STYLE = """
    QGroupBox {
        font-weight: bold;
        font-size: 12px;
        border: 1px solid #c0c0c0;
        border-radius: 6px;
        margin-top: 10px;
        padding-top: 14px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 6px;
        color: #333;
    }
"""

DARK_GROUP_STYLE = """
    QGroupBox {
        font-weight: bold;
        font-size: 12px;
        border: 1px solid #555;
        border-radius: 6px;
        margin-top: 10px;
        padding-top: 14px;
        background-color: #333;
        color: #e0e0e0;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 6px;
        color: #ccc;
    }
"""

LIGHT_HELP_BUTTON_STYLE = """
    QToolButton {
        background: #e0e0e0;
        border: 1px solid #aaa;
        border-radius: 11px;
        font-weight: bold;
        font-size: 11px;
        color: #444;
    }
    QToolButton:hover {
        background: #cde4ff;
        border-color: #4a90d9;
        color: #1a1a1a;
    }
    QToolTip {
        background-color: #2b2b2b;
        color: #e0e0e0;
        border: 1px solid #555;
        padding: 8px;
        font-size: 12px;
    }
"""

DARK_HELP_BUTTON_STYLE = """
    QToolButton {
        background: #4a4a4a;
        border: 1px solid #666;
        border-radius: 11px;
        font-weight: bold;
        font-size: 11px;
        color: #ccc;
    }
    QToolButton:hover {
        background: #3a5a8a;
        border-color: #5a9fd4;
        color: #fff;
    }
    QToolTip {
        background-color: #3c3c3c;
        color: #e0e0e0;
        border: 1px solid #555;
        padding: 8px;
        font-size: 12px;
    }
"""

LIGHT_START_BUTTON_STYLE = """
    QPushButton {
        background-color: #2e7d32;
        color: white;
        font-size: 14px;
        font-weight: bold;
        padding: 8px 24px;
        border: none;
        border-radius: 6px;
    }
    QPushButton:hover {
        background-color: #388e3c;
    }
    QPushButton:pressed {
        background-color: #1b5e20;
    }
    QPushButton:disabled {
        background-color: #999;
    }
"""

DARK_START_BUTTON_STYLE = """
    QPushButton {
        background-color: #2e7d32;
        color: white;
        font-size: 14px;
        font-weight: bold;
        padding: 8px 24px;
        border: none;
        border-radius: 6px;
    }
    QPushButton:hover {
        background-color: #388e3c;
    }
    QPushButton:pressed {
        background-color: #1b5e20;
    }
    QPushButton:disabled {
        background-color: #555;
        color: #888;
    }
"""

LIGHT_CANCEL_BUTTON_STYLE = """
    QPushButton {
        background-color: #c62828;
        color: white;
        font-size: 14px;
        font-weight: bold;
        padding: 8px 24px;
        border: none;
        border-radius: 6px;
    }
    QPushButton:hover {
        background-color: #e53935;
    }
    QPushButton:pressed {
        background-color: #b71c1c;
    }
    QPushButton:disabled {
        background-color: #999;
    }
"""

DARK_CANCEL_BUTTON_STYLE = """
    QPushButton {
        background-color: #c62828;
        color: white;
        font-size: 14px;
        font-weight: bold;
        padding: 8px 24px;
        border: none;
        border-radius: 6px;
    }
    QPushButton:hover {
        background-color: #e53935;
    }
    QPushButton:pressed {
        background-color: #b71c1c;
    }
    QPushButton:disabled {
        background-color: #555;
        color: #888;
    }
"""

LIGHT_PROGRESS_STYLE = """
    QProgressBar {
        border: 1px solid #c0c0c0;
        border-radius: 4px;
        text-align: center;
        height: 22px;
        background: #f0f0f0;
    }
    QProgressBar::chunk {
        background-color: #4caf50;
        border-radius: 3px;
    }
"""

DARK_PROGRESS_STYLE = """
    QProgressBar {
        border: 1px solid #555;
        border-radius: 4px;
        text-align: center;
        height: 22px;
        background: #3c3c3c;
        color: #e0e0e0;
    }
    QProgressBar::chunk {
        background-color: #4caf50;
        border-radius: 3px;
    }
"""

LIGHT_FILELIST_STYLE = """
    QListWidget {
        border: 1px solid #c0c0c0;
        border-radius: 4px;
        background: #fff;
        font-size: 11px;
    }
    QListWidget::item {
        padding: 2px 4px;
    }
    QListWidget::item:selected {
        background: #cde4ff;
    }
"""

DARK_FILELIST_STYLE = """
    QListWidget {
        border: 1px solid #555;
        border-radius: 4px;
        background: #333;
        color: #e0e0e0;
        font-size: 11px;
    }
    QListWidget::item {
        padding: 2px 4px;
    }
    QListWidget::item:selected {
        background: #3a5a8a;
        color: #fff;
    }
"""

LIGHT_STATUSBAR_STYLE = "QStatusBar { border-top: 1px solid #d0d0d0; color: #555; }"
DARK_STATUSBAR_STYLE = "QStatusBar { border-top: 1px solid #555; color: #aaa; background: #2b2b2b; }"

LIGHT_FILECOUNT_STYLE = "color: #666; font-style: italic;"
DARK_FILECOUNT_STYLE = "color: #aaa; font-style: italic;"
