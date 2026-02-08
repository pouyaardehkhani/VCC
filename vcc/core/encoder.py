"""
FFmpeg encoder worker - runs encoding in a background thread, emitting signals for UI updates.
"""

import os
import glob
import shutil
import subprocess
from PyQt6.QtCore import QThread, pyqtSignal


def find_ffmpeg() -> str:
    """
    Locate ffmpeg executable. Checks:
    1. System PATH (shutil.which)
    2. Winget install locations
    3. Common manual install folders
    Returns the full path to ffmpeg.exe, or 'ffmpeg' as fallback.
    """
    # 1. Check PATH
    path = shutil.which("ffmpeg")
    if path:
        return path

    # 2. Winget shim directory
    winget_links = os.path.expandvars(
        r"%LOCALAPPDATA%\Microsoft\WinGet\Links\ffmpeg.exe"
    )
    if os.path.isfile(winget_links):
        return winget_links

    # 3. Winget package directories (version-agnostic glob)
    winget_pkgs = os.path.expandvars(
        r"%LOCALAPPDATA%\Microsoft\WinGet\Packages"
    )
    for pattern in [
        os.path.join(winget_pkgs, "Gyan.FFmpeg*", "ffmpeg-*", "bin", "ffmpeg.exe"),
        os.path.join(winget_pkgs, "Gyan.FFmpeg*", "ffmpeg.exe"),
    ]:
        matches = glob.glob(pattern)
        if matches:
            return matches[0]

    # 4. Common manual install locations
    for candidate in [
        r"C:\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
    ]:
        if os.path.isfile(candidate):
            return candidate

    return "ffmpeg"  # fallback — let subprocess raise FileNotFoundError


class EncoderWorker(QThread):
    """
    Runs FFmpeg encoding for a list of files.
    Emits signals for log output, progress, and completion.
    """

    log_output = pyqtSignal(str)        # raw line from ffmpeg
    file_started = pyqtSignal(int, int, str)  # index, total, filename
    file_finished = pyqtSignal(int, int, str, bool)  # index, total, filename, success
    encoding_done = pyqtSignal()        # all files done
    encoding_error = pyqtSignal(str)    # fatal error message

    def __init__(
        self,
        files: list[str],
        output_dir: str,
        width: int,
        height: int,
        codec: str,
        codec_params: dict[str, str],
        pix_fmt: str,
        audio_codec: str = "copy",
        subtitle_codec: str = "copy",
        fps: str = "",
        bitrate: str = "",
        overwrite: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self.files = files
        self.output_dir = output_dir
        self.width = width
        self.height = height
        self.codec = codec
        self.codec_params = codec_params  # {"preset": "8", "crf": "32", ...}
        self.pix_fmt = pix_fmt
        self.audio_codec = audio_codec
        self.subtitle_codec = subtitle_codec
        self.fps = fps          # e.g. "24", "30", "60", or "" for default
        self.bitrate = bitrate  # e.g. "1M", "5M", or "" for default
        self.overwrite = overwrite
        self._cancelled = False
        self._ffmpeg_path = find_ffmpeg()

    def cancel(self):
        self._cancelled = True
        if hasattr(self, "_process") and self._process and self._process.poll() is None:
            self._process.terminate()

    def build_ffmpeg_args(self, src: str, dst: str) -> list[str]:
        """Build the ffmpeg argument list for a single file."""
        ow_flag = "-y" if self.overwrite else "-n"
        scale_filter = f"scale={self.width}:{self.height}"
        has_bitrate = bool(self.bitrate and self.bitrate.strip())

        args = [
            self._ffmpeg_path,
            "-hide_banner",
            ow_flag,
            "-i", src,
            "-map_metadata", "0",
            "-map_chapters", "0",
            "-map", "0:v:0",
            "-map", "0:a?",
            "-map", "0:s?",
            "-vf", scale_filter,
            "-c:v", self.codec,
        ]

        # Frame rate
        if self.fps and self.fps.strip():
            args.extend(["-r", self.fps.strip()])

        # Total video bitrate
        if has_bitrate:
            args.extend(["-b:v", self.bitrate.strip()])

        # Add codec-specific params (skip empty tune etc.)
        # When using target bitrate mode, skip CRF/quality params
        # as they conflict with bitrate-based rate control.
        quality_keys = {"crf", "qp", "q:v"}
        for key, value in self.codec_params.items():
            if value is not None and str(value).strip():
                if key in quality_keys and has_bitrate:
                    continue  # skip quality param in bitrate mode
                args.extend([f"-{key}", str(value)])

        # When using bitrate with SVT-AV1, set rate control to VBR (rc=1)
        # SVT-AV1 defaults to CQ mode (rc=0) which rejects -b:v
        if has_bitrate and self.codec == "libsvtav1":
            args.extend(["-svtav1-params", "rc=1"])

        if self.pix_fmt and self.pix_fmt.strip():
            args.extend(["-pix_fmt", self.pix_fmt])

        args.extend([
            "-c:a", self.audio_codec,
            "-c:s", self.subtitle_codec,
            dst,
        ])

        return args

    def make_output_name(self, src_path: str) -> str:
        """Generate output filename like: basename.WxH.codec.paramN.mkv"""
        base = os.path.splitext(os.path.basename(src_path))[0]
        label = f"{self.width}x{self.height}"

        # Build param suffix
        param_parts = []
        for key, value in self.codec_params.items():
            if value is not None and str(value).strip():
                param_parts.append(f"{key}{value}")

        if self.fps and self.fps.strip():
            param_parts.append(f"{self.fps.strip()}fps")
        if self.bitrate and self.bitrate.strip():
            param_parts.append(f"br{self.bitrate.strip()}")

        param_str = ".".join(param_parts) if param_parts else ""
        if param_str:
            name = f"{base}.{label}.{self.codec}.{param_str}.mkv"
        else:
            name = f"{base}.{label}.{self.codec}.mkv"

        return os.path.join(self.output_dir, name)

    def run(self):
        total = len(self.files)
        try:
            os.makedirs(self.output_dir, exist_ok=True)
        except Exception as e:
            self.encoding_error.emit(f"Cannot create output directory: {e}")
            self.encoding_done.emit()
            return

        for idx, src in enumerate(self.files, 1):
            if self._cancelled:
                self.log_output.emit("\n--- Encoding cancelled by user ---\n")
                break

            filename = os.path.basename(src)
            dst = self.make_output_name(src)

            if os.path.exists(dst) and not self.overwrite:
                self.log_output.emit(f"[{idx}/{total}] SKIP (exists): {filename}\n")
                self.file_finished.emit(idx, total, filename, True)
                continue

            self.file_started.emit(idx, total, filename)
            self.log_output.emit(f"[{idx}/{total}] ENCODE: {filename}\n")

            args = self.build_ffmpeg_args(src, dst)
            cmd_display = " ".join(f'"{a}"' if " " in a else a for a in args)
            self.log_output.emit(f"> {cmd_display}\n\n")

            try:
                self._process = subprocess.Popen(
                    args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                )

                for line in self._process.stdout:
                    if self._cancelled:
                        self._process.terminate()
                        break
                    self.log_output.emit(line)

                self._process.wait()
                success = self._process.returncode == 0

                if not success and not self._cancelled:
                    self.log_output.emit(
                        f"\n[WARNING] FFmpeg exited with code {self._process.returncode} on: {filename}\n"
                    )
                elif success:
                    self.log_output.emit(f"\nDone -> {os.path.basename(dst)}\n")

                self.file_finished.emit(idx, total, filename, success)

            except FileNotFoundError:
                self.encoding_error.emit(
                    "ffmpeg not found! Please install FFmpeg and ensure ffmpeg.exe is in your system PATH."
                )
                self.encoding_done.emit()
                return
            except Exception as e:
                self.log_output.emit(f"\n[ERROR] {e}\n")
                self.file_finished.emit(idx, total, filename, False)

            self.log_output.emit("\n")

        if not self._cancelled:
            self.log_output.emit("=== All done. ===\n")
        self.encoding_done.emit()
