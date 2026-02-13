"""
Main window for Video Codec Converter (VCC).
"""

import os
import json
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QPushButton, QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit,
    QGroupBox, QFileDialog, QMessageBox, QMenuBar, QMenu,
    QProgressBar, QSplitter, QListWidget, QAbstractItemView,
    QToolButton, QSizePolicy, QCheckBox, QApplication, QListWidgetItem,
    QDialog, QTimeEdit, QDialogButtonBox, QFormLayout, QInputDialog,
)
from PyQt6.QtCore import Qt, QSize, QEvent, QSettings, QTime, QMimeData, QUrl
from PyQt6.QtGui import QAction, QFont, QIcon, QDragEnterEvent, QDropEvent

from vcc.core.codecs import CODECS
from vcc.core.pixel_formats import PIXEL_FORMATS, query_encoder_pix_fmts
from vcc.core.encoder import EncoderWorker
from vcc.core.gpu_detect import (
    probe_available_gpu_encoders, get_gpu_encoder, is_gpu_encoder, GpuEncoder,
)
from vcc.ui.terminal_widget import TerminalWidget
from vcc.ui.help_dialogs import (
    CodecHelpDialog, PixelFormatHelpDialog, AudioHelpDialog,
    ResolutionHelpDialog, FPSHelpDialog, BitrateHelpDialog, AboutDialog,
    GPUEncodingHelpDialog, OutputFormatHelpDialog,
)
from vcc.ui.themes import (
    LIGHT_THEME, DARK_THEME,
    LIGHT_MENUBAR_STYLE, DARK_MENUBAR_STYLE,
    LIGHT_GROUP_STYLE, DARK_GROUP_STYLE,
    LIGHT_HELP_BUTTON_STYLE, DARK_HELP_BUTTON_STYLE,
    LIGHT_START_BUTTON_STYLE, DARK_START_BUTTON_STYLE,
    LIGHT_CANCEL_BUTTON_STYLE, DARK_CANCEL_BUTTON_STYLE,
    LIGHT_PROGRESS_STYLE, DARK_PROGRESS_STYLE,
    LIGHT_FILELIST_STYLE, DARK_FILELIST_STYLE,
    LIGHT_STATUSBAR_STYLE, DARK_STATUSBAR_STYLE,
    LIGHT_FILECOUNT_STYLE, DARK_FILECOUNT_STYLE,
    get_arrow_stylesheet,
)


# ---------------------------------------------------------------------------
# Scroll-proof widgets: ignore mouse wheel so scrolling the form
# doesn't accidentally change values.
# ---------------------------------------------------------------------------
class NoScrollSpinBox(QSpinBox):
    """QSpinBox that ignores wheel events unless it has focus."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, event):
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()


class NoScrollDoubleSpinBox(QDoubleSpinBox):
    """QDoubleSpinBox that ignores wheel events unless it has focus."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, event):
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()


class NoScrollComboBox(QComboBox):
    """QComboBox that always ignores wheel events to prevent accidental changes."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, event):
        event.ignore()


# ---------------------------------------------------------------------------
# Tooltip button helper
# ---------------------------------------------------------------------------
def make_help_button(tooltip_text: str, dark: bool = False) -> QToolButton:
    """Create a small '?' button with a rich tooltip."""
    btn = QToolButton()
    btn.setText(" ? ")
    btn.setFixedSize(QSize(22, 22))
    btn.setToolTip(tooltip_text)
    btn.setStyleSheet(DARK_HELP_BUTTON_STYLE if dark else LIGHT_HELP_BUTTON_STYLE)
    return btn


# ---------------------------------------------------------------------------
# Trim Dialog
# ---------------------------------------------------------------------------
class TrimDialog(QDialog):
    """Dialog for specifying start/end trim times."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Video Trimming")
        self.setFixedSize(380, 200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        lbl = QLabel("Specify start and/or end times to trim the video.\n"
                      "Leave at 00:00:00 to skip that boundary.")
        lbl.setWordWrap(True)
        layout.addWidget(lbl)

        form = QFormLayout()
        form.setSpacing(8)

        self._start_time = QTimeEdit()
        self._start_time.setDisplayFormat("HH:mm:ss")
        self._start_time.setTime(QTime(0, 0, 0))
        form.addRow("Start Time:", self._start_time)

        self._end_time = QTimeEdit()
        self._end_time.setDisplayFormat("HH:mm:ss")
        self._end_time.setTime(QTime(0, 0, 0))
        form.addRow("End Time:", self._end_time)

        layout.addLayout(form)

        btn_row = QHBoxLayout()
        self._btn_clear = QPushButton("Clear Trim")
        self._btn_clear.clicked.connect(self._clear)
        btn_row.addWidget(self._btn_clear)
        btn_row.addStretch()

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        btn_row.addWidget(buttons)
        layout.addLayout(btn_row)

    def _clear(self):
        self._start_time.setTime(QTime(0, 0, 0))
        self._end_time.setTime(QTime(0, 0, 0))

    def get_times(self) -> tuple[str, str]:
        """Return (start, end) as HH:MM:SS strings, or empty if 00:00:00."""
        s = self._start_time.time()
        e = self._end_time.time()
        start = "" if s == QTime(0, 0, 0) else s.toString("HH:mm:ss")
        end = "" if e == QTime(0, 0, 0) else e.toString("HH:mm:ss")
        return start, end

    def set_times(self, start: str, end: str):
        if start:
            self._start_time.setTime(QTime.fromString(start, "HH:mm:ss"))
        if end:
            self._end_time.setTime(QTime.fromString(end, "HH:mm:ss"))


# ---------------------------------------------------------------------------
# Codec parameter widgets
# ---------------------------------------------------------------------------
class CodecParamWidget(QWidget):
    """Dynamic widget row for a single codec parameter."""

    def __init__(self, key: str, param_def: dict, parent=None):
        super().__init__(parent)
        self.key = key
        self.param_def = param_def

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)

        label = QLabel(param_def["label"] + ":")
        label.setFixedWidth(130)
        layout.addWidget(label)

        ptype = param_def["type"]
        if ptype == "int":
            self.editor = NoScrollSpinBox()
            self.editor.setMinimum(param_def.get("min", 0))
            self.editor.setMaximum(param_def.get("max", 100))
            self.editor.setValue(param_def.get("default", 0))
            self.editor.setFixedWidth(100)
        elif ptype == "choice":
            self.editor = NoScrollComboBox()
            choices = param_def.get("choices", [])
            for c in choices:
                display = c if c else "(none)"
                self.editor.addItem(display, c)
            default = param_def.get("default", "")
            idx = self.editor.findData(default)
            if idx >= 0:
                self.editor.setCurrentIndex(idx)
            self.editor.setFixedWidth(140)
        else:
            self.editor = QLineEdit()
            self.editor.setText(str(param_def.get("default", "")))
            self.editor.setFixedWidth(140)

        layout.addWidget(self.editor)

        # '?' help button
        help_btn = make_help_button(param_def.get("tooltip", ""))
        layout.addWidget(help_btn)

        layout.addStretch()

    def get_value(self) -> str:
        if isinstance(self.editor, QSpinBox):
            return str(self.editor.value())
        elif isinstance(self.editor, QComboBox):
            return self.editor.currentData() or ""
        else:
            return self.editor.text().strip()


# ---------------------------------------------------------------------------
# Main Window
# ---------------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Codec Converter (VCC)")
        self.setMinimumSize(900, 700)
        self.resize(1050, 780)

        # Set window icon
        import sys
        icon_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "icon.ico")
        if not os.path.isfile(icon_path):
            # Try relative to this module (dev mode)
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "icon.ico")
        if os.path.isfile(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Enable drag & drop on the main window
        self.setAcceptDrops(True)

        self._worker: EncoderWorker | None = None
        self._codec_param_widgets: list[CodecParamWidget] = []

        # Per-file trim state: { filepath: (start_str, end_str) }
        self._file_trims: dict[str, tuple[str, str]] = {}

        # Load theme preference
        self._settings = QSettings("VCC", "VideoCodecConverter")
        self._dark_mode = self._settings.value("dark_mode", False, type=bool)

        self._build_menu_bar()
        self._build_ui()
        self._connect_signals()

        # Trigger initial codec param build
        self._on_codec_changed()

        # Apply saved theme
        self._apply_theme()

    # ------------------------------------------------------------------
    # Menu bar
    # ------------------------------------------------------------------
    def _build_menu_bar(self):
        menubar = self.menuBar()

        # File
        file_menu = menubar.addMenu("File")
        self._act_open = QAction("Open Files...", self)
        self._act_open.setShortcut("Ctrl+O")
        file_menu.addAction(self._act_open)
        self._act_open_dir = QAction("Open Input Directory...", self)
        file_menu.addAction(self._act_open_dir)
        file_menu.addSeparator()
        act_exit = QAction("Exit", self)
        act_exit.setShortcut("Alt+F4")
        act_exit.triggered.connect(self.close)
        file_menu.addAction(act_exit)

        # Edit
        edit_menu = menubar.addMenu("Edit")
        self._act_clear_files = QAction("Clear File List", self)
        edit_menu.addAction(self._act_clear_files)
        self._act_clear_terminal = QAction("Clear Terminal", self)
        edit_menu.addAction(self._act_clear_terminal)

        # Presets
        presets_menu = menubar.addMenu("Presets")
        self._act_save_preset = QAction("Save Current Settings...", self)
        self._act_save_preset.setShortcut("Ctrl+S")
        presets_menu.addAction(self._act_save_preset)
        self._act_load_preset = QAction("Load Preset...", self)
        self._act_load_preset.setShortcut("Ctrl+L")
        presets_menu.addAction(self._act_load_preset)
        self._act_delete_preset = QAction("Delete Preset...", self)
        presets_menu.addAction(self._act_delete_preset)

        # Settings
        settings_menu = menubar.addMenu("Settings")
        self._act_dark_mode = QAction("Dark Mode", self)
        self._act_dark_mode.setCheckable(True)
        self._act_dark_mode.setChecked(self._dark_mode)
        settings_menu.addAction(self._act_dark_mode)
        settings_menu.addSeparator()
        self._act_reset_defaults = QAction("Reset to Defaults", self)
        settings_menu.addAction(self._act_reset_defaults)

        # Help
        help_menu = menubar.addMenu("Help")
        self._act_help_codec = QAction("Codec Information...", self)
        help_menu.addAction(self._act_help_codec)
        self._act_help_pixfmt = QAction("Pixel Format Information...", self)
        help_menu.addAction(self._act_help_pixfmt)
        self._act_help_audio = QAction("Audio Codec Information...", self)
        help_menu.addAction(self._act_help_audio)
        self._act_help_resolution = QAction("Resolution Guide...", self)
        help_menu.addAction(self._act_help_resolution)
        self._act_help_fps = QAction("Frame Rate (FPS) Guide...", self)
        help_menu.addAction(self._act_help_fps)
        self._act_help_bitrate = QAction("Video Bitrate Guide...", self)
        help_menu.addAction(self._act_help_bitrate)
        self._act_help_gpu = QAction("GPU Encoding Guide...", self)
        help_menu.addAction(self._act_help_gpu)
        self._act_help_output_format = QAction("Output Format Guide...", self)
        help_menu.addAction(self._act_help_output_format)
        help_menu.addSeparator()
        self._act_about = QAction("About VCC...", self)
        help_menu.addAction(self._act_about)

    # ------------------------------------------------------------------
    # Central UI
    # ------------------------------------------------------------------
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(8)

        main_vlayout = QVBoxLayout()
        main_vlayout.setContentsMargins(0, 0, 0, 0)
        main_vlayout.setSpacing(6)

        # ---- Top panel: settings (scrollable) ----
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(6)

        # --- Input section ---
        input_group = QGroupBox("Input")
        ig_layout = QVBoxLayout(input_group)

        # File selection row
        file_row = QHBoxLayout()
        self._btn_add_files = QPushButton("Add Files...")
        self._btn_add_files.setFixedWidth(110)
        file_row.addWidget(self._btn_add_files)
        self._btn_add_dir = QPushButton("Add Directory...")
        self._btn_add_dir.setFixedWidth(130)
        file_row.addWidget(self._btn_add_dir)
        self._btn_remove_selected = QPushButton("Remove Selected")
        self._btn_remove_selected.setFixedWidth(130)
        file_row.addWidget(self._btn_remove_selected)
        self._btn_clear_files = QPushButton("Clear All")
        self._btn_clear_files.setFixedWidth(90)
        file_row.addWidget(self._btn_clear_files)
        file_row.addStretch()
        self._lbl_file_count = QLabel("0 files")
        file_row.addWidget(self._lbl_file_count)
        ig_layout.addLayout(file_row)

        # File list
        self._file_list = QListWidget()
        self._file_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._file_list.setMinimumHeight(80)
        self._file_list.setMaximumHeight(150)
        ig_layout.addWidget(self._file_list)
        top_layout.addWidget(input_group)

        # --- Output section ---
        output_group = QGroupBox("Output")
        og_layout = QHBoxLayout(output_group)
        og_layout.addWidget(QLabel("Output Directory:"))
        self._txt_output_dir = QLineEdit()
        self._txt_output_dir.setPlaceholderText("Select output directory...")
        og_layout.addWidget(self._txt_output_dir)
        self._btn_output_dir = QPushButton("Browse...")
        self._btn_output_dir.setFixedWidth(90)
        og_layout.addWidget(self._btn_output_dir)
        self._chk_overwrite = QCheckBox("Overwrite existing")
        og_layout.addWidget(self._chk_overwrite)

        og_layout.addSpacing(12)
        og_layout.addWidget(QLabel("Format:"))
        self._cmb_output_format = NoScrollComboBox()
        self._cmb_output_format.setFixedWidth(100)
        self._output_formats = [
            ("Auto", ""),
            ("MKV", "mkv"),
            ("MP4", "mp4"),
            ("WebM", "webm"),
            ("AVI", "avi"),
            ("MOV", "mov"),
            ("TS", "ts"),
            ("FLV", "flv"),
            ("WMV", "wmv"),
            ("OGG", "ogg"),
            ("M4V", "m4v"),
            ("MPG", "mpg"),
            ("3GP", "3gp"),
            ("MXF", "mxf"),
        ]
        for name, val in self._output_formats:
            self._cmb_output_format.addItem(name, val)
        self._cmb_output_format.setCurrentIndex(0)
        og_layout.addWidget(self._cmb_output_format)

        self._chk_concat = QCheckBox("Merge/Concatenate files")
        self._chk_concat.setToolTip(
            "Concatenate all input files into a single output file\n"
            "using FFmpeg's concat demuxer (stream copy, no re-encode).\n"
            "Files should have similar formats for best results."
        )
        og_layout.addWidget(self._chk_concat)

        top_layout.addWidget(output_group)

        # --- Encoding settings ---
        enc_group = QGroupBox("Encoding Settings")
        enc_vlayout = QVBoxLayout(enc_group)
        enc_vlayout.setSpacing(8)

        # Row 0: Resolution
        row_res = QHBoxLayout()
        lbl_preset_res = QLabel("Resolution:")
        lbl_preset_res.setFixedWidth(100)
        row_res.addWidget(lbl_preset_res)
        self._cmb_resolution_preset = NoScrollComboBox()
        self._cmb_resolution_preset.setFixedWidth(180)
        self._resolution_presets = [
            ("Custom",       None,  None),
            ("8K UHD",       7680, 4320),
            ("4K UHD",       3840, 2160),
            ("4K DCI",       4096, 2160),
            ("1440p QHD",    2560, 1440),
            ("1080p Full HD",1920, 1080),
            ("720p HD",      1280,  720),
            ("480p SD",       854,  480),
            ("480p (4:3)",    640,  480),
            ("360p",          640,  360),
            ("240p",          426,  240),
            ("UWQHD 21:9",  3440, 1440),
            ("UWHD 21:9",   2560, 1080),
            ("Vertical 1080×1920", 1080, 1920),
            ("Square 1080×1080",   1080, 1080),
        ]
        for name, w, h in self._resolution_presets:
            if w is None:
                self._cmb_resolution_preset.addItem(name)
            else:
                self._cmb_resolution_preset.addItem(f"{name}  ({w}×{h})")
        # default to 720p HD (index 6)
        self._cmb_resolution_preset.setCurrentIndex(6)
        row_res.addWidget(self._cmb_resolution_preset)
        row_res.addSpacing(20)
        lbl_w = QLabel("Width:")
        lbl_w.setFixedWidth(45)
        row_res.addWidget(lbl_w)
        self._spn_width = NoScrollSpinBox()
        self._spn_width.setRange(128, 7680)
        self._spn_width.setValue(1280)
        self._spn_width.setSuffix(" px")
        self._spn_width.setFixedWidth(110)
        row_res.addWidget(self._spn_width)
        row_res.addSpacing(12)
        lbl_h = QLabel("Height:")
        lbl_h.setFixedWidth(50)
        row_res.addWidget(lbl_h)
        self._spn_height = NoScrollSpinBox()
        self._spn_height.setRange(128, 4320)
        self._spn_height.setValue(720)
        self._spn_height.setSuffix(" px")
        self._spn_height.setFixedWidth(110)
        row_res.addWidget(self._spn_height)
        row_res.addSpacing(8)
        res_help = make_help_button(
            "Output video resolution in pixels.\n\n"
            "Common values:\n"
            "  3840x2160 = 4K UHD\n"
            "  2560x1440 = 1440p QHD\n"
            "  1920x1080 = 1080p Full HD\n"
            "  1280x720  = 720p HD\n"
            "  854x480   = 480p SD"
        )
        row_res.addWidget(res_help)
        row_res.addStretch()
        enc_vlayout.addLayout(row_res)

        # Row 1: Codec
        row_codec = QHBoxLayout()
        lbl_codec = QLabel("Video Codec:")
        lbl_codec.setFixedWidth(100)
        row_codec.addWidget(lbl_codec)
        self._cmb_codec = NoScrollComboBox()
        self._cmb_codec.setMinimumWidth(250)
        self._cmb_codec.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # CPU codecs
        for ffname, info in CODECS.items():
            self._cmb_codec.addItem(f"{info['display']}  ({ffname})", ffname)

        # GPU codecs (auto-detected)
        self._gpu_encoders = probe_available_gpu_encoders()
        if self._gpu_encoders:
            self._cmb_codec.insertSeparator(self._cmb_codec.count())
            for gpu_enc in self._gpu_encoders:
                self._cmb_codec.addItem(
                    f"\U0001F3AE {gpu_enc.display_name}  ({gpu_enc.name})",
                    gpu_enc.name,
                )

        idx = self._cmb_codec.findData("libsvtav1")
        if idx >= 0:
            self._cmb_codec.setCurrentIndex(idx)
        row_codec.addWidget(self._cmb_codec)
        row_codec.addSpacing(8)
        codec_help_btn = make_help_button(
            "The video codec (encoder) determines compression\n"
            "efficiency, quality, speed, and compatibility.\n\n"
            "See Help → Codec Information for a full comparison."
        )
        row_codec.addWidget(codec_help_btn)
        enc_vlayout.addLayout(row_codec)

        # Row 2: Pixel format
        row_pixfmt = QHBoxLayout()
        lbl_pf = QLabel("Pixel Format:")
        lbl_pf.setFixedWidth(100)
        row_pixfmt.addWidget(lbl_pf)
        self._cmb_pixfmt = NoScrollComboBox()
        self._cmb_pixfmt.setEditable(False)
        self._cmb_pixfmt.setMinimumWidth(300)
        self._cmb_pixfmt.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        for pf in PIXEL_FORMATS:
            ffname, display, bits, sub, alpha, desc = pf
            self._cmb_pixfmt.addItem(f"{ffname}  —  {display}", ffname)
        pf_idx = self._cmb_pixfmt.findData("yuv420p10le")
        if pf_idx >= 0:
            self._cmb_pixfmt.setCurrentIndex(pf_idx)
        row_pixfmt.addWidget(self._cmb_pixfmt)
        row_pixfmt.addSpacing(8)
        pixfmt_help_btn = make_help_button(
            "Pixel format defines color model, chroma subsampling,\n"
            "bit depth, and alpha channel.\n\n"
            "See Help → Pixel Format Information for details."
        )
        row_pixfmt.addWidget(pixfmt_help_btn)
        enc_vlayout.addLayout(row_pixfmt)

        # Row 3: Audio / Subtitle codec
        row_audio = QHBoxLayout()
        lbl_audio = QLabel("Audio:")
        lbl_audio.setFixedWidth(100)
        row_audio.addWidget(lbl_audio)
        self._cmb_audio = NoScrollComboBox()
        self._cmb_audio.setEditable(False)
        self._cmb_audio.addItems(["copy", "aac", "libopus", "libvorbis", "ac3", "flac", "pcm_s16le"])
        self._cmb_audio.setCurrentText("copy")
        self._cmb_audio.setFixedWidth(150)
        row_audio.addWidget(self._cmb_audio)
        row_audio.addSpacing(20)
        lbl_sub = QLabel("Subtitles:")
        lbl_sub.setFixedWidth(65)
        row_audio.addWidget(lbl_sub)
        self._cmb_subtitle = NoScrollComboBox()
        self._cmb_subtitle.setEditable(False)
        self._cmb_subtitle.addItems(["copy", "ass", "srt", "mov_text", "none"])
        self._cmb_subtitle.setCurrentText("copy")
        self._cmb_subtitle.setFixedWidth(150)
        row_audio.addWidget(self._cmb_subtitle)
        row_audio.addSpacing(8)
        audio_help = make_help_button(
            "Audio codec: 'copy' = keep original audio (no re-encode).\n"
            "Other options re-encode the audio stream.\n\n"
            "Subtitle codec: 'copy' = keep original subtitles.\n"
            "'none' = strip subtitles entirely.\n\n"
            "See Help → Audio Codec Information for details."
        )
        row_audio.addWidget(audio_help)
        row_audio.addStretch()
        enc_vlayout.addLayout(row_audio)

        # Row 4: FPS
        row_fps = QHBoxLayout()
        lbl_fps = QLabel("Frame Rate:")
        lbl_fps.setFixedWidth(100)
        row_fps.addWidget(lbl_fps)
        self._cmb_fps = NoScrollComboBox()
        self._cmb_fps.setFixedWidth(180)
        self._fps_presets = [
            ("Default (keep original)", ""),
            ("12 fps",      "12"),
            ("15 fps",      "15"),
            ("18 fps",      "18"),
            ("20 fps",      "20"),
            ("23.976 fps",  "23.976"),
            ("24 fps",      "24"),
            ("25 fps (PAL)","25"),
            ("29.97 fps",   "29.97"),
            ("30 fps",      "30"),
            ("50 fps",      "50"),
            ("60 fps",      "60"),
            ("Custom",      "__custom__"),
        ]
        for name, val in self._fps_presets:
            self._cmb_fps.addItem(name, val)
        self._cmb_fps.setCurrentIndex(0)
        row_fps.addWidget(self._cmb_fps)
        row_fps.addSpacing(8)
        self._spn_custom_fps = NoScrollDoubleSpinBox()
        self._spn_custom_fps.setRange(1.0, 300.0)
        self._spn_custom_fps.setDecimals(3)
        self._spn_custom_fps.setValue(30.0)
        self._spn_custom_fps.setSuffix(" fps")
        self._spn_custom_fps.setFixedWidth(120)
        self._spn_custom_fps.setEnabled(False)
        self._spn_custom_fps.setToolTip("Enter a custom frame rate value (1–300).")
        row_fps.addWidget(self._spn_custom_fps)
        row_fps.addSpacing(8)
        fps_help = make_help_button(
            "Output frame rate (Frames Per Second).\n\n"
            "Default = keep the original video frame rate.\n"
            "Custom = enter any value between 1 and 300.\n"
            "Lower FPS = smaller files, choppier motion.\n"
            "Higher FPS = smoother motion, larger files.\n\n"
            "See Help \u2192 Frame Rate (FPS) Guide for details."
        )
        row_fps.addWidget(fps_help)
        row_fps.addStretch()
        enc_vlayout.addLayout(row_fps)

        # Row 5: Bitrate
        row_bitrate = QHBoxLayout()
        lbl_br = QLabel("Bitrate:")
        lbl_br.setFixedWidth(100)
        row_bitrate.addWidget(lbl_br)
        self._cmb_bitrate = NoScrollComboBox()
        self._cmb_bitrate.setFixedWidth(180)
        self._bitrate_presets = [
            ("Default (CRF mode)",  ""),
            ("256K",   "256K"),
            ("384K",   "384K"),
            ("512K",   "512K"),
            ("768K",   "768K"),
            ("1M",     "1M"),
            ("1.5M",   "1500K"),
            ("2M",     "2M"),
            ("5M",     "5M"),
            ("10M",    "10M"),
            ("15M",    "15M"),
            ("20M",    "20M"),
        ]
        for name, val in self._bitrate_presets:
            self._cmb_bitrate.addItem(name, val)
        self._cmb_bitrate.setCurrentIndex(0)
        row_bitrate.addWidget(self._cmb_bitrate)
        row_bitrate.addSpacing(8)
        br_help = make_help_button(
            "Target video bitrate.\n\n"
            "Default = use CRF / constant quality mode\n"
            "(bitrate is auto-adjusted for consistent quality).\n\n"
            "Selecting a specific bitrate switches to\n"
            "target bitrate mode with predictable file sizes.\n\n"
            "See Help \u2192 Video Bitrate Guide for details."
        )
        row_bitrate.addWidget(br_help)
        row_bitrate.addStretch()
        enc_vlayout.addLayout(row_bitrate)

        # Row 6: Trim
        row_trim = QHBoxLayout()
        lbl_trim = QLabel("Trim:")
        lbl_trim.setFixedWidth(100)
        row_trim.addWidget(lbl_trim)
        self._btn_trim = QPushButton("Set Trim...")
        self._btn_trim.setFixedWidth(120)
        self._btn_trim.setToolTip("Open a dialog to set start/end trim times.")
        row_trim.addWidget(self._btn_trim)
        self._lbl_trim_info = QLabel("No trim set")
        self._lbl_trim_info.setStyleSheet("color: #888; font-style: italic;")
        row_trim.addSpacing(12)
        row_trim.addWidget(self._lbl_trim_info)
        row_trim.addStretch()
        enc_vlayout.addLayout(row_trim)

        top_layout.addWidget(enc_group)

        # --- Codec-specific parameters (dynamic) ---
        self._codec_params_group = QGroupBox("Codec Parameters")
        self._codec_params_layout = QVBoxLayout(self._codec_params_group)
        top_layout.addWidget(self._codec_params_group)

        # --- Action buttons ---
        action_row = QHBoxLayout()
        self._btn_start = QPushButton("  Start Encoding  ")
        action_row.addWidget(self._btn_start)

        self._btn_cancel = QPushButton("  Cancel  ")
        self._btn_cancel.setEnabled(False)
        action_row.addWidget(self._btn_cancel)

        action_row.addStretch()

        # Batch progress bar
        batch_prog_row = QHBoxLayout()
        batch_prog_row.setSpacing(4)
        self._lbl_batch_progress = QLabel("Batch:")
        batch_prog_row.addWidget(self._lbl_batch_progress)
        self._progress = QProgressBar()
        self._progress.setFixedWidth(250)
        self._progress.setTextVisible(True)
        self._progress.setValue(0)
        batch_prog_row.addWidget(self._progress)
        action_row.addLayout(batch_prog_row)

        top_layout.addLayout(action_row)

        # Wrap top panel in scroll area so it never clips
        scroll_area = QScrollArea()
        scroll_area.setWidget(top_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_vlayout.addWidget(scroll_area, stretch=3)

        # ---- Bottom panel: terminal ----
        terminal_group = QGroupBox("FFmpeg Output")
        tg_layout = QVBoxLayout(terminal_group)
        self._terminal = TerminalWidget()
        self._terminal.setMinimumHeight(120)
        tg_layout.addWidget(self._terminal)
        main_vlayout.addWidget(terminal_group, stretch=2)

        root_layout.addLayout(main_vlayout)

        # Status bar
        self.statusBar().showMessage("Ready")

    # ------------------------------------------------------------------
    # Styling / Theme
    # ------------------------------------------------------------------
    def _apply_theme(self):
        """Apply the current theme (light or dark) to the entire UI."""
        app = QApplication.instance()
        dark = self._dark_mode

        # Apply global app stylesheet + arrow images
        theme = DARK_THEME if dark else LIGHT_THEME
        arrows = get_arrow_stylesheet(dark)
        app.setStyleSheet(theme + arrows)

        # Menu bar
        self.menuBar().setStyleSheet(DARK_MENUBAR_STYLE if dark else LIGHT_MENUBAR_STYLE)

        # File list
        self._file_list.setStyleSheet(DARK_FILELIST_STYLE if dark else LIGHT_FILELIST_STYLE)

        # File count label
        self._lbl_file_count.setStyleSheet(DARK_FILECOUNT_STYLE if dark else LIGHT_FILECOUNT_STYLE)

        # Start / Cancel buttons
        self._btn_start.setStyleSheet(DARK_START_BUTTON_STYLE if dark else LIGHT_START_BUTTON_STYLE)
        self._btn_cancel.setStyleSheet(DARK_CANCEL_BUTTON_STYLE if dark else LIGHT_CANCEL_BUTTON_STYLE)

        # Progress bar
        self._progress.setStyleSheet(DARK_PROGRESS_STYLE if dark else LIGHT_PROGRESS_STYLE)

        # Status bar
        self.statusBar().setStyleSheet(DARK_STATUSBAR_STYLE if dark else LIGHT_STATUSBAR_STYLE)

        # Update all '?' help buttons
        style = DARK_HELP_BUTTON_STYLE if dark else LIGHT_HELP_BUTTON_STYLE
        for btn in self.findChildren(QToolButton):
            if btn.text().strip() == "?":
                btn.setStyleSheet(style)

    def _toggle_dark_mode(self, checked: bool):
        """Toggle between dark and light themes."""
        self._dark_mode = checked
        self._settings.setValue("dark_mode", checked)
        self._apply_theme()

    # ------------------------------------------------------------------
    # Signal connections
    # ------------------------------------------------------------------
    def _connect_signals(self):
        # Menu actions
        self._act_open.triggered.connect(self._add_files)
        self._act_open_dir.triggered.connect(self._add_directory)
        self._act_clear_files.triggered.connect(self._clear_files)
        self._act_clear_terminal.triggered.connect(self._terminal.clear_terminal)
        self._act_reset_defaults.triggered.connect(self._reset_defaults)
        self._act_dark_mode.triggered.connect(self._toggle_dark_mode)
        self._act_help_codec.triggered.connect(lambda: CodecHelpDialog(self).exec())
        self._act_help_pixfmt.triggered.connect(lambda: PixelFormatHelpDialog(self).exec())
        self._act_help_audio.triggered.connect(lambda: AudioHelpDialog(self).exec())
        self._act_help_resolution.triggered.connect(lambda: ResolutionHelpDialog(self).exec())
        self._act_help_fps.triggered.connect(lambda: FPSHelpDialog(self).exec())
        self._act_help_bitrate.triggered.connect(lambda: BitrateHelpDialog(self).exec())
        self._act_help_gpu.triggered.connect(lambda: GPUEncodingHelpDialog(self).exec())
        self._act_help_output_format.triggered.connect(lambda: OutputFormatHelpDialog(self).exec())
        self._act_about.triggered.connect(lambda: AboutDialog(self).exec())

        # Presets
        self._act_save_preset.triggered.connect(self._save_preset)
        self._act_load_preset.triggered.connect(self._load_preset)
        self._act_delete_preset.triggered.connect(self._delete_preset)

        # Buttons
        self._btn_add_files.clicked.connect(self._add_files)
        self._btn_add_dir.clicked.connect(self._add_directory)
        self._btn_remove_selected.clicked.connect(self._remove_selected_files)
        self._btn_clear_files.clicked.connect(self._clear_files)
        self._btn_output_dir.clicked.connect(self._browse_output)
        self._btn_start.clicked.connect(self._start_encoding)
        self._btn_cancel.clicked.connect(self._cancel_encoding)
        self._btn_trim.clicked.connect(self._open_trim_dialog)

        # Codec change -> rebuild params
        self._cmb_codec.currentIndexChanged.connect(self._on_codec_changed)

        # FPS preset -> enable/disable custom spinbox
        self._cmb_fps.currentIndexChanged.connect(self._on_fps_preset_changed)

        # Resolution preset -> set width/height
        self._cmb_resolution_preset.currentIndexChanged.connect(self._on_resolution_preset_changed)
        # Width/Height manual change -> switch preset to "Custom"
        self._spn_width.valueChanged.connect(self._on_resolution_manual_change)
        self._spn_height.valueChanged.connect(self._on_resolution_manual_change)

    # ------------------------------------------------------------------
    # Drag & Drop
    # ------------------------------------------------------------------
    _DRAG_VIDEO_EXTS = {".mkv", ".mp4", ".avi", ".mov", ".m4v", ".webm",
                        ".ts", ".flv", ".wmv", ".mpg", ".mpeg"}

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            # Only accept if at least one URL is a video file or directory
            dominated = False
            for url in event.mimeData().urls():
                p = url.toLocalFile()
                if os.path.isdir(p):
                    dominated = True
                    break
                if os.path.isfile(p) and os.path.splitext(p)[1].lower() in self._DRAG_VIDEO_EXTS:
                    dominated = True
                    break
            if dominated:
                event.acceptProposedAction()
            else:
                event.ignore()

    def dropEvent(self, event: QDropEvent):
        paths = []
        for url in event.mimeData().urls():
            p = url.toLocalFile()
            if os.path.isfile(p):
                ext = os.path.splitext(p)[1].lower()
                if ext in self._DRAG_VIDEO_EXTS:
                    paths.append(p)
            elif os.path.isdir(p):
                for root, _dirs, fnames in os.walk(p):
                    for fn in sorted(fnames):
                        if os.path.splitext(fn)[1].lower() in self._DRAG_VIDEO_EXTS:
                            paths.append(os.path.join(root, fn))
        if paths:
            self._append_files(paths)
            self.statusBar().showMessage(f"Added {len(paths)} file(s) via drag & drop")
        event.acceptProposedAction()

    # ------------------------------------------------------------------
    # Trim dialog
    # ------------------------------------------------------------------
    def _open_trim_dialog(self):
        """Open a trim dialog for the selected file(s) in the input list."""
        selected = self._file_list.selectedItems()
        if not selected:
            if self._file_list.count() == 0:
                QMessageBox.information(self, "No Files", "Please add video files first.")
                return
            # If nothing selected, ask user to select
            QMessageBox.information(
                self, "Select File",
                "Please select one or more files in the input list to set trim times."
            )
            return

        for item in selected:
            filepath = item.data(Qt.ItemDataRole.UserRole)
            filename = os.path.basename(filepath)
            existing = self._file_trims.get(filepath, ("", ""))
            dlg = TrimDialog(self)
            dlg.setWindowTitle(f"Trim — {filename}")
            dlg.set_times(existing[0], existing[1])
            if dlg.exec() == QDialog.DialogCode.Accepted:
                start, end = dlg.get_times()
                if start or end:
                    self._file_trims[filepath] = (start, end)
                else:
                    self._file_trims.pop(filepath, None)
            else:
                break  # user cancelled, stop iterating
        self._update_trim_label()

    def _update_trim_label(self):
        trimmed_count = len(self._file_trims)
        if trimmed_count > 0:
            self._lbl_trim_info.setText(f"{trimmed_count} file(s) trimmed")
            self._lbl_trim_info.setStyleSheet("color: #2e7d32; font-weight: bold;")
        else:
            self._lbl_trim_info.setText("No trim set")
            self._lbl_trim_info.setStyleSheet("color: #888; font-style: italic;")

    # ------------------------------------------------------------------
    # Preset Profiles
    # ------------------------------------------------------------------
    def _get_presets_dir(self) -> str:
        """Return path to presets directory (next to the settings)."""
        base = os.path.join(os.path.expanduser("~"), ".vcc_presets")
        os.makedirs(base, exist_ok=True)
        return base

    def _gather_current_settings(self) -> dict:
        """Gather all current encoding settings into a dict."""
        return {
            "resolution_preset_idx": self._cmb_resolution_preset.currentIndex(),
            "width": self._spn_width.value(),
            "height": self._spn_height.value(),
            "codec_idx": self._cmb_codec.currentIndex(),
            "pixfmt_text": self._cmb_pixfmt.currentText(),
            "audio": self._cmb_audio.currentText(),
            "subtitle": self._cmb_subtitle.currentText(),
            "fps_idx": self._cmb_fps.currentIndex(),
            "custom_fps": self._spn_custom_fps.value(),
            "bitrate_idx": self._cmb_bitrate.currentIndex(),
            "output_format_idx": self._cmb_output_format.currentIndex(),
            "overwrite": self._chk_overwrite.isChecked(),
            "concat": self._chk_concat.isChecked(),
            "trim_start": "",
            "trim_end": "",
        }

    def _apply_settings(self, settings: dict):
        """Apply a settings dict to the UI."""
        try:
            self._cmb_resolution_preset.setCurrentIndex(settings.get("resolution_preset_idx", 6))
            self._spn_width.setValue(settings.get("width", 1280))
            self._spn_height.setValue(settings.get("height", 720))
            ci = settings.get("codec_idx", 0)
            if ci < self._cmb_codec.count():
                self._cmb_codec.setCurrentIndex(ci)
            pf_text = settings.get("pixfmt_text", "")
            if pf_text:
                idx = self._cmb_pixfmt.findText(pf_text)
                if idx >= 0:
                    self._cmb_pixfmt.setCurrentIndex(idx)
            self._cmb_audio.setCurrentText(settings.get("audio", "copy"))
            self._cmb_subtitle.setCurrentText(settings.get("subtitle", "copy"))
            self._cmb_fps.setCurrentIndex(settings.get("fps_idx", 0))
            self._spn_custom_fps.setValue(settings.get("custom_fps", 30.0))
            self._cmb_bitrate.setCurrentIndex(settings.get("bitrate_idx", 0))
            ofi = settings.get("output_format_idx", 0)
            if ofi < self._cmb_output_format.count():
                self._cmb_output_format.setCurrentIndex(ofi)
            self._chk_overwrite.setChecked(settings.get("overwrite", False))
            self._chk_concat.setChecked(settings.get("concat", False))
            # Presets don't store per-file trims – just clear
            self._file_trims.clear()
            self._update_trim_label()
            self._on_fps_preset_changed(self._cmb_fps.currentIndex())
        except Exception:
            pass

    def _save_preset(self):
        name, ok = QInputDialog.getText(self, "Save Preset", "Preset name:")
        if not ok or not name.strip():
            return
        name = name.strip()
        settings = self._gather_current_settings()
        path = os.path.join(self._get_presets_dir(), f"{name}.json")
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
            self.statusBar().showMessage(f"Preset '{name}' saved")
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Could not save preset:\n{e}")

    def _load_preset(self):
        presets_dir = self._get_presets_dir()
        files = [f[:-5] for f in os.listdir(presets_dir) if f.endswith(".json")]
        if not files:
            QMessageBox.information(self, "No Presets", "No saved presets found.\n\nUse Presets → Save Current Settings to create one.")
            return
        name, ok = QInputDialog.getItem(self, "Load Preset", "Select preset:", files, 0, False)
        if not ok:
            return
        path = os.path.join(presets_dir, f"{name}.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                settings = json.load(f)
            self._apply_settings(settings)
            self.statusBar().showMessage(f"Preset '{name}' loaded")
        except Exception as e:
            QMessageBox.warning(self, "Load Error", f"Could not load preset:\n{e}")

    def _delete_preset(self):
        presets_dir = self._get_presets_dir()
        files = [f[:-5] for f in os.listdir(presets_dir) if f.endswith(".json")]
        if not files:
            QMessageBox.information(self, "No Presets", "No saved presets found.")
            return
        name, ok = QInputDialog.getItem(self, "Delete Preset", "Select preset to delete:", files, 0, False)
        if not ok:
            return
        path = os.path.join(presets_dir, f"{name}.json")
        try:
            os.remove(path)
            self.statusBar().showMessage(f"Preset '{name}' deleted")
        except Exception as e:
            QMessageBox.warning(self, "Delete Error", f"Could not delete preset:\n{e}")

    # ------------------------------------------------------------------
    # File management
    # ------------------------------------------------------------------
    _VIDEO_EXTENSIONS = (
        "Video Files (*.mkv *.mp4 *.avi *.mov *.m4v *.webm *.ts *.flv *.wmv *.mpg *.mpeg);;"
        "All Files (*.*)"
    )

    def _add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Video Files", "", self._VIDEO_EXTENSIONS
        )
        if files:
            self._append_files(files)

    def _add_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Input Directory")
        if dir_path:
            exts = {".mkv", ".mp4", ".avi", ".mov", ".m4v", ".webm", ".ts", ".flv", ".wmv", ".mpg", ".mpeg"}
            found = []
            for root, _dirs, fnames in os.walk(dir_path):
                for fn in sorted(fnames):
                    if os.path.splitext(fn)[1].lower() in exts:
                        found.append(os.path.join(root, fn))
            if found:
                self._append_files(found)
            else:
                QMessageBox.information(self, "No Videos", "No video files found in the selected directory.")

    def _append_files(self, paths: list[str]):
        existing = set()
        for i in range(self._file_list.count()):
            existing.add(self._file_list.item(i).data(Qt.ItemDataRole.UserRole))
        for p in paths:
            if p not in existing:
                item = QListWidgetItem(p)
                item.setData(Qt.ItemDataRole.UserRole, p)
                self._file_list.addItem(item)
        self._update_file_count()

    def _remove_selected_files(self):
        for item in self._file_list.selectedItems():
            filepath = item.data(Qt.ItemDataRole.UserRole)
            self._file_trims.pop(filepath, None)
            self._file_list.takeItem(self._file_list.row(item))
        self._update_file_count()
        self._update_trim_label()

    def _clear_files(self):
        self._file_list.clear()
        self._file_trims.clear()
        self._update_file_count()
        self._update_trim_label()

    def _update_file_count(self):
        count = self._file_list.count()
        self._lbl_file_count.setText(f"{count} file{'s' if count != 1 else ''}")

    def _browse_output(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self._txt_output_dir.setText(dir_path)

    # ------------------------------------------------------------------
    # Codec parameter panel (dynamic)
    # ------------------------------------------------------------------
    def _on_codec_changed(self):
        # Remove old param widgets
        for w in self._codec_param_widgets:
            self._codec_params_layout.removeWidget(w)
            w.deleteLater()
        self._codec_param_widgets.clear()

        codec_key = self._cmb_codec.currentData()
        if not codec_key:
            self._codec_params_layout.addStretch()
            return

        gpu_enc = get_gpu_encoder(codec_key)
        if gpu_enc:
            # ── GPU encoder: build preset + quality widgets ──
            # Preset widget
            preset_def = {
                "label": "Preset",
                "type": gpu_enc.preset_type,
                "tooltip": gpu_enc.preset_tooltip,
            }
            if gpu_enc.preset_type == "choice":
                preset_def["choices"] = gpu_enc.preset_values
                preset_def["default"] = gpu_enc.preset_default
            else:
                preset_def["default"] = gpu_enc.preset_default
                preset_def["min"] = 0
                preset_def["max"] = 100
            pw = CodecParamWidget(gpu_enc.preset_key, preset_def)
            self._codec_params_layout.addWidget(pw)
            self._codec_param_widgets.append(pw)

            # Quality widget
            quality_def = {
                "label": gpu_enc.quality_label,
                "type": "int",
                "default": gpu_enc.quality_default,
                "min": gpu_enc.quality_min,
                "max": gpu_enc.quality_max,
                "tooltip": gpu_enc.quality_tooltip,
            }
            qw = CodecParamWidget(gpu_enc.quality_param, quality_def)
            self._codec_params_layout.addWidget(qw)
            self._codec_param_widgets.append(qw)

            # GPU indicator label
            vendor_icons = {"NVIDIA": "\U0001F7E2", "AMD": "\U0001F534", "Intel": "\U0001F535"}
            icon = vendor_icons.get(gpu_enc.vendor, "\U0001F3AE")
            lbl = QLabel(f"{icon} GPU Encoding ({gpu_enc.vendor}) — Near-zero CPU usage, 10–50× faster")
            lbl.setStyleSheet("font-style: italic; padding: 4px 0;")
            self._codec_params_layout.addWidget(lbl)
            self._codec_param_widgets.append(lbl)
        elif codec_key in CODECS:
            # ── CPU encoder: use CODECS dict ──
            params = CODECS[codec_key].get("params", {})
            for pkey, pdef in params.items():
                widget = CodecParamWidget(pkey, pdef)
                self._codec_params_layout.addWidget(widget)
                self._codec_param_widgets.append(widget)

        # Filter pixel format dropdown for the selected encoder
        self._update_pixfmt_combo(codec_key)

        # Filter output format dropdown for the selected codec
        self._update_output_format_combo(codec_key)

        # Add stretch at end
        self._codec_params_layout.addStretch()

    # Codec family → compatible output containers
    _CODEC_FORMAT_MAP: dict[str, set[str]] = {
        # H.264 works in almost everything
        "h264": {"mkv", "mp4", "avi", "mov", "ts", "flv", "wmv", "m4v", "mpg", "3gp", "mxf"},
        # H.265/HEVC
        "hevc": {"mkv", "mp4", "mov", "ts", "m4v", "mxf"},
        # AV1
        "av1":  {"mkv", "mp4", "webm"},
        # VP9
        "vp9":  {"mkv", "webm"},
        # MPEG-4 Part 2
        "mpeg4": {"mkv", "mp4", "avi", "mov", "ts", "flv", "3gp", "mpg"},
        # H.266/VVC — very limited container support
        "vvc":  {"mkv", "ts"},
    }
    # Map specific encoder names to codec families
    _ENCODER_FAMILY: dict[str, str] = {
        "libx264": "h264", "h264_nvenc": "h264", "h264_amf": "h264", "h264_qsv": "h264",
        "libx265": "hevc", "hevc_nvenc": "hevc", "hevc_amf": "hevc", "hevc_qsv": "hevc",
        "libsvtav1": "av1", "libaom-av1": "av1", "librav1e": "av1",
        "av1_nvenc": "av1", "av1_amf": "av1", "av1_qsv": "av1",
        "libvpx-vp9": "vp9",
        "mpeg4": "mpeg4",
        "libvvenc": "vvc",
    }

    def _update_output_format_combo(self, encoder_name: str):
        """Filter output format dropdown to only show containers compatible with the codec."""
        family = self._ENCODER_FAMILY.get(encoder_name, "")
        allowed = self._CODEC_FORMAT_MAP.get(family)

        # Remember current selection
        prev_data = self._cmb_output_format.currentData()

        self._cmb_output_format.blockSignals(True)
        self._cmb_output_format.clear()
        # Auto is always available
        self._cmb_output_format.addItem("Auto", "")
        for name, val in self._output_formats:
            if not val:
                continue  # skip Auto, already added
            if allowed is None or val in allowed:
                self._cmb_output_format.addItem(name, val)
        self._cmb_output_format.blockSignals(False)

        # Restore previous selection if still available
        idx = self._cmb_output_format.findData(prev_data)
        self._cmb_output_format.setCurrentIndex(max(idx, 0))

    def _update_pixfmt_combo(self, encoder_name: str):
        """Filter pixel format dropdown to only show formats the encoder supports.

        GPU encoders: filter by bit-depth capability.  FFmpeg auto-converts
        pixel format names (e.g. yuv420p10le → p010le) so the exact native
        format list is not the right filter — only bit depth matters.

        CPU encoders: use FFmpeg's reported "Supported pixel formats" list,
        which accurately reflects what the software encoder can handle.
        """
        gpu_enc = get_gpu_encoder(encoder_name)

        if gpu_enc:
            # GPU: filter by max bit depth (H.264 = 8-bit only, HEVC/AV1 = 10-bit)
            max_depth = gpu_enc.max_bit_depth
            accept = lambda pf: pf[2] <= max_depth  # pf[2] = bit_depth
        else:
            # CPU: use FFmpeg's exact supported format list
            supported = query_encoder_pix_fmts(encoder_name)
            if supported is not None:
                accept = lambda pf: pf[0] in supported
            else:
                accept = lambda pf: True  # query failed → show all

        # Remember current selection so we can try to restore it
        previous = self._cmb_pixfmt.currentData()

        self._cmb_pixfmt.blockSignals(True)
        self._cmb_pixfmt.clear()

        for pf in PIXEL_FORMATS:
            if accept(pf):
                ffname, display = pf[0], pf[1]
                self._cmb_pixfmt.addItem(f"{ffname}  —  {display}", ffname)

        # Try to restore previous selection
        idx = self._cmb_pixfmt.findData(previous)
        if idx >= 0:
            self._cmb_pixfmt.setCurrentIndex(idx)
        else:
            # Previous format not available — pick the best default
            # Prefer yuv420p (universal) then first item
            fallback = self._cmb_pixfmt.findData("yuv420p")
            self._cmb_pixfmt.setCurrentIndex(fallback if fallback >= 0 else 0)

        self._cmb_pixfmt.blockSignals(False)

    # ------------------------------------------------------------------
    # Resolution preset helpers
    # ------------------------------------------------------------------
    def _on_fps_preset_changed(self, index: int):
        """Enable/disable the custom FPS spinbox based on preset selection."""
        data = self._cmb_fps.currentData()
        self._spn_custom_fps.setEnabled(data == "__custom__")

    def _get_selected_fps(self) -> str:
        """Return the FPS value to use: preset value or custom spinbox."""
        data = self._cmb_fps.currentData()
        if data == "__custom__":
            val = self._spn_custom_fps.value()
            # Format nicely: strip trailing zeros
            if val == int(val):
                return str(int(val))
            return f"{val:.3f}".rstrip('0').rstrip('.')
        return data or ""

    def _on_resolution_preset_changed(self, index: int):
        """When a resolution preset is selected, auto-fill Width/Height."""
        if index < 0 or index >= len(self._resolution_presets):
            return
        _, w, h = self._resolution_presets[index]
        if w is None or h is None:
            return  # "Custom" – do nothing
        # Block signals on spinboxes so they don't trigger _on_resolution_manual_change
        self._spn_width.blockSignals(True)
        self._spn_height.blockSignals(True)
        self._spn_width.setValue(w)
        self._spn_height.setValue(h)
        self._spn_width.blockSignals(False)
        self._spn_height.blockSignals(False)

    def _on_resolution_manual_change(self):
        """When Width or Height is changed manually, switch preset to Custom."""
        self._cmb_resolution_preset.blockSignals(True)
        self._cmb_resolution_preset.setCurrentIndex(0)  # "Custom"
        self._cmb_resolution_preset.blockSignals(False)

    # ------------------------------------------------------------------
    # Defaults
    # ------------------------------------------------------------------
    def _reset_defaults(self):
        self._cmb_resolution_preset.setCurrentIndex(6)  # 720p HD
        self._spn_width.setValue(1280)
        self._spn_height.setValue(720)
        idx = self._cmb_codec.findData("libsvtav1")
        if idx >= 0:
            self._cmb_codec.setCurrentIndex(idx)
        pf_idx = self._cmb_pixfmt.findData("yuv420p10le")
        if pf_idx >= 0:
            self._cmb_pixfmt.setCurrentIndex(pf_idx)
        self._cmb_audio.setCurrentText("copy")
        self._cmb_subtitle.setCurrentText("copy")
        self._cmb_fps.setCurrentIndex(0)
        self._spn_custom_fps.setValue(30.0)
        self._spn_custom_fps.setEnabled(False)
        self._cmb_bitrate.setCurrentIndex(0)
        self._cmb_output_format.setCurrentIndex(0)
        self._chk_overwrite.setChecked(False)
        self._chk_concat.setChecked(False)
        self._file_trims.clear()
        self._update_trim_label()
        self._on_codec_changed()
        self.statusBar().showMessage("Settings reset to defaults")

    # ------------------------------------------------------------------
    # Encoding
    # ------------------------------------------------------------------
    def _get_selected_pixfmt(self) -> str:
        """Get pixel format - either from combo data or custom text."""
        data = self._cmb_pixfmt.currentData()
        if data:
            return data
        return self._cmb_pixfmt.currentText().strip()

    def _start_encoding(self):
        # Validate
        if self._file_list.count() == 0:
            QMessageBox.warning(self, "No Files", "Please add video files to encode.")
            return

        output_dir = self._txt_output_dir.text().strip()
        if not output_dir:
            QMessageBox.warning(self, "No Output", "Please select an output directory.")
            return

        # Gather files
        files = []
        for i in range(self._file_list.count()):
            files.append(self._file_list.item(i).data(Qt.ItemDataRole.UserRole))

        # Gather codec params
        codec_params = {}
        for pw in self._codec_param_widgets:
            if isinstance(pw, CodecParamWidget):
                codec_params[pw.key] = pw.get_value()

        codec_key = self._cmb_codec.currentData()
        pix_fmt = self._get_selected_pixfmt()

        # Special VP9 handling: need -b:v 0 for CRF mode
        if codec_key == "libvpx-vp9" and "crf" in codec_params:
            codec_params["b:v"] = "0"

        # Create worker
        self._worker = EncoderWorker(
            files=files,
            output_dir=output_dir,
            width=self._spn_width.value(),
            height=self._spn_height.value(),
            codec=codec_key,
            codec_params=codec_params,
            pix_fmt=pix_fmt,
            audio_codec=self._cmb_audio.currentText().strip() or "copy",
            subtitle_codec=self._cmb_subtitle.currentText().strip() or "copy",
            fps=self._get_selected_fps(),
            bitrate=self._cmb_bitrate.currentData() or "",
            overwrite=self._chk_overwrite.isChecked(),
            output_format=self._cmb_output_format.currentData() or "",
            file_trims=self._file_trims,
            concatenate=self._chk_concat.isChecked(),
        )

        self._worker.log_output.connect(self._terminal.append_text)
        self._worker.file_started.connect(self._on_file_started)
        self._worker.file_finished.connect(self._on_file_finished)
        self._worker.encoding_done.connect(self._on_encoding_done)
        self._worker.encoding_error.connect(self._on_encoding_error)

        self._progress.setMaximum(len(files))
        self._progress.setValue(0)
        self._btn_start.setEnabled(False)
        self._btn_cancel.setEnabled(True)
        self.statusBar().showMessage("Encoding...")

        self._terminal.clear_terminal()
        self._terminal.append_text(f"Starting encoding of {len(files)} file(s)...\n\n")

        self._worker.start()

    def _cancel_encoding(self):
        if self._worker:
            self._worker.cancel()
        self._btn_cancel.setEnabled(False)
        self.statusBar().showMessage("Cancelling...")

    def _on_file_started(self, idx, total, name):
        self.statusBar().showMessage(f"[{idx}/{total}] Encoding: {name}")

    def _on_file_finished(self, idx, total, name, success):
        self._progress.setValue(idx)

    def _on_encoding_done(self):
        self._btn_start.setEnabled(True)
        self._btn_cancel.setEnabled(False)
        self._cleanup_worker()
        self.statusBar().showMessage("Encoding complete")

    def _on_encoding_error(self, msg):
        QMessageBox.critical(self, "FFmpeg Error", msg)
        self._btn_start.setEnabled(True)
        self._btn_cancel.setEnabled(False)
        self._cleanup_worker()
        self.statusBar().showMessage("Error occurred")

    def _cleanup_worker(self):
        """Safely clean up the encoder worker thread."""
        if self._worker is not None:
            self._worker.wait(5000)  # wait for thread to fully finish
            self._worker.deleteLater()  # schedule safe Qt deletion
            self._worker = None

    # ------------------------------------------------------------------
    # Close event
    # ------------------------------------------------------------------
    def closeEvent(self, event):
        if self._worker and self._worker.isRunning():
            reply = QMessageBox.question(
                self,
                "Encoding in Progress",
                "Encoding is still running. Cancel and exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._worker.cancel()
                self._worker.wait(5000)
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
