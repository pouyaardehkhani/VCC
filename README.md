# Video Codec Converter (VCC)

A desktop GUI application for batch video transcoding using **FFmpeg**. VCC provides a user-friendly interface to convert video files between popular codecs with full control over encoding parameters.

![Platform](https://img.shields.io/badge/platform-Windows-blue)
![Python](https://img.shields.io/badge/python-3.12-green)
![License](https://img.shields.io/badge/license-MIT-brightgreen)
![Release](https://img.shields.io/badge/release-v1.0.0-orange)

---

## Features

- **7 Video Codecs** — AV1 (SVT-AV1), H.264, H.265/HEVC, VP9, AV1 (libaom), MPEG-4, AV1 (rav1e)
- **15 Pixel Formats** — yuv420p, yuv420p10le, yuv444p, and more
- **Audio Control** — Copy, re-encode (AAC/Opus/MP3/FLAC/Vorbis), or remove audio
- **Resolution Presets** — Quick presets for 360p through 8K, or set custom dimensions
- **Subtitle Handling** — Copy subtitles or remove them
- **Batch Processing** — Select multiple files or entire directories
- **Embedded Terminal** — Live FFmpeg output displayed in the app
- **Built-in Help** — Menu bar with Codec, Pixel Format, Audio, and Resolution guides
- **Scroll-safe Controls** — Mouse wheel won't change values unless a control is focused
- **Single EXE** — Standalone `.exe`, no Python installation required for end users

---

## Demo

https://github.com/pouyaardehkhani/VCC/raw/master/demo/demo.mp4

> Click the video above to see VCC in action.

---

## Installation for End Users

### Prerequisites

| Requirement | Version | Download |
|---|---|---|
| **FFmpeg** | **7.1.x** (full build recommended) | [gyan.dev/ffmpeg](https://www.gyan.dev/ffmpeg/builds/) or [ffmpeg.org](https://ffmpeg.org/download.html) |
| **Windows** | 10 or 11 (64-bit) | — |

> **Important:** FFmpeg must be version **7.1.x** (full build from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) is recommended). This is the version the application was developed and tested against. The full build includes all codec libraries (libsvtav1, libx264, libx265, libvpx, libaom, librav1e, etc.).

### Step 1 — Install FFmpeg

**Option A: Manual install**
1. Download **ffmpeg-7.1.1-full_build.7z** from [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/)
2. Extract the archive (e.g. to `C:\ffmpeg`)
3. Add the `bin` folder (`C:\ffmpeg\bin`) to your system **PATH**:
   - Search "Environment Variables" in Windows Start menu
   - Edit the `Path` variable under System variables
   - Add `C:\ffmpeg\bin`
4. Verify by opening a new Command Prompt and running:
   ```
   ffmpeg -version
   ```
   You should see `ffmpeg version 7.1.1-full_build` or similar.

**Option B: Using winget (Windows Package Manager)**
```
winget install Gyan.FFmpeg
```
Then verify:
```
ffmpeg -version
```

### Step 2 — Download VCC

1. Go to the [Releases](../../releases) page
2. Download `VideoCodecConverter-v1.0.0.zip` from the latest release
3. Extract the ZIP
4. Double-click **`VideoCodecConverter.exe`** — no installation needed

> **Note:** Windows SmartScreen may show a warning the first time you run the EXE. Click **"More info" → "Run anyway"** to proceed.

---

## Supported Codecs

| Codec | FFmpeg Encoder | Container | Use Case |
|---|---|---|---|
| AV1 (SVT-AV1) | `libsvtav1` | `.mkv` | Best quality/size ratio, modern |
| H.264 | `libx264` | `.mp4` | Maximum compatibility |
| H.265 / HEVC | `libx265` | `.mp4` | Good compression, wide support |
| VP9 | `libvpx-vp9` | `.webm` | Web video, YouTube |
| AV1 (libaom) | `libaom-av1` | `.mkv` | Reference AV1 encoder (slow) |
| MPEG-4 | `mpeg4` | `.mp4` | Legacy compatibility |
| AV1 (rav1e) | `librav1e` | `.mkv` | Rust-based AV1 encoder |

---

## Building from Source (for Developers)

### Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.12.x |
| pip | Latest |
| FFmpeg | 7.1.x (on PATH) |

### Setup

```bash
cd VCC

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run from Source

```bash
python run.pyw
```

### Build Standalone EXE

```bash
python -m PyInstaller --onefile --windowed --name VideoCodecConverter --noconfirm --clean run.pyw
```

The EXE will be created at `dist/VideoCodecConverter.exe`.

---

## Project Structure

```
VCC/
├── vcc/                        # Application source code
│   ├── core/
│   │   ├── codecs.py           # Codec definitions and help text
│   │   ├── pixel_formats.py    # Pixel format definitions
│   │   └── encoder.py          # FFmpeg worker thread
│   └── ui/
│       ├── main_window.py      # Main application window
│       ├── terminal_widget.py  # Embedded terminal output
│       └── help_dialogs.py     # Help dialog windows
├── run.pyw                     # Entry point (no console window)
├── run.py                      # Entry point (with console, for debugging)
├── build.py                    # Build script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| EXE won't start, missing DLL error | Install [Microsoft Visual C++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist) |
| "ffmpeg is not recognized" | Add FFmpeg's `bin` folder to your system PATH and restart the terminal |
| Windows SmartScreen blocks EXE | Click "More info" → "Run anyway" |
| Encoding fails with codec error | Ensure you have the **full build** of FFmpeg (not essentials) which includes all codec libraries |

---

## License

MIT License — free for personal and commercial use.

---

## Version History

- **v1.0.0** — Initial release with full GUI, 7 codecs, batch processing, resolution presets, and standalone EXE
