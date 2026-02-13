# Video Codec Converter (VCC)

<p align="center">
  <img src="icon.png" alt="VCC Logo" width="720" height="300">
</p>

A desktop GUI application for batch video transcoding using **FFmpeg**. VCC provides a user-friendly interface to convert video files between popular codecs with full control over encoding parameters.

![Platform](https://img.shields.io/badge/platform-Windows-blue)
![Python](https://img.shields.io/badge/python-3.12-green)
![License](https://img.shields.io/badge/license-MIT-brightgreen)
![Release](https://img.shields.io/badge/release-v1.2-orange)

---

## Features

- **8 Video Codecs** — AV1 (SVT-AV1), H.264, H.265/HEVC, H.266/VVC, VP9, AV1 (libaom), MPEG-4, AV1 (rav1e)
- **GPU Encoding** — Auto-detected NVIDIA NVENC, AMD AMF, and Intel QSV hardware encoders (10–50× faster)
- **15 Pixel Formats** — yuv420p, yuv420p10le, yuv444p, and more
- **Audio Control** — Copy, re-encode (AAC/Opus/MP3/FLAC/Vorbis), or remove audio
- **Resolution Presets** — Quick presets for 360p through 8K, or set custom dimensions
- **Subtitle Handling** — Copy subtitles or remove them
- **Batch Processing** — Select multiple files or entire directories
- **Drag & Drop** — Drop video files or folders directly onto the window
- **Batch Progress Bar** — Overall progress across all files in the queue
- **Preset Profiles** — Save and load your encoding settings (Presets menu)
- **Video Trimming** — Set start/end times to trim videos during conversion
- **Output Format Selection** — Choose from 14 container formats (MKV, MP4, WebM, AVI, MOV, TS, FLV, WMV, OGG, M4V, MPG, 3GP, MXF) which are codec-aware or auto-detect
- **Concatenate / Merge** — Merge multiple video files into a single output file
- **Embedded Terminal** — Live FFmpeg output displayed in the app
- **Built-in Help** — Menu bar with Codec, Pixel Format, Audio, Resolution, FPS, Bitrate, and GPU Encoding guides
- **Dark / Light Theme** — Toggle between dark and light mode via Settings menu (preference saved across sessions)
- **Scroll-safe Controls** — Mouse wheel won't accidentally change dropdown values
- **Single EXE** — Standalone `.exe`, no Python installation required for end users

---

## Installation for End Users

### Prerequisites

| Requirement | Version | Download |
|---|---|---|
| **FFmpeg** | **8.x** (full build recommended) | [gyan.dev/ffmpeg](https://www.gyan.dev/ffmpeg/builds/) or [ffmpeg.org](https://ffmpeg.org/download.html) |
| **Windows** | 10 or 11 (64-bit) | — |

> **Important:** The full build is required (not essentials) to include all codec libraries.

### Step 1 — Install FFmpeg

**Option A: Using winget (easiest)**
```
winget install ffmpeg
```
Verify:
```
ffmpeg -version
```

**Option B: Manual install**
1. Download the latest **full_build** from [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/)
2. Extract the archive (e.g. to `C:\ffmpeg`)
3. Add the `bin` folder (`C:\ffmpeg\bin`) to your system **PATH**:
   - Search "Environment Variables" in Windows Start menu
   - Edit the `Path` variable under System variables
   - Add `C:\ffmpeg\bin`
4. Verify by opening a new Command Prompt and running:
   ```
   ffmpeg -version
   ```

> **Note:** VCC automatically detects FFmpeg in common locations including winget install paths.

### Step 2 — Download VCC

1. Go to the [Releases](../../releases) page
2. Download **`VideoCodecConverter.exe`** from the latest release
3. Double-click to run — no installation needed

> **Note:** Windows SmartScreen may show a warning the first time you run the EXE. Click **"More info" → "Run anyway"** to proceed.

---

## Supported Codecs

### CPU Encoders

| Codec | FFmpeg Encoder | Container | Use Case |
|---|---|---|---|
| AV1 (SVT-AV1) | `libsvtav1` | `.mkv` | Best quality/size ratio, modern |
| H.264 | `libx264` | `.mkv` | Maximum compatibility |
| H.265 / HEVC | `libx265` | `.mkv` | Good compression, wide support |
| **H.266 / VVC** | `libvvenc` | `.mkv` | **Next-gen, best compression (new!)** |
| VP9 | `libvpx-vp9` | `.webm` | Web video, YouTube |
| AV1 (libaom) | `libaom-av1` | `.mkv` | Reference AV1 encoder (slow) |
| MPEG-4 | `mpeg4` | `.mkv` | Legacy compatibility |
| AV1 (rav1e) | `librav1e` | `.mkv` | Rust-based AV1 encoder |

### GPU Encoders (Auto-Detected)

| Codec | NVIDIA (NVENC) | AMD (AMF) | Intel (QSV) |
|---|---|---|---|
| H.264 | `h264_nvenc` | `h264_amf` | `h264_qsv` |
| H.265 / HEVC | `hevc_nvenc` | `hevc_amf` | `hevc_qsv` |
| AV1 | `av1_nvenc` (RTX 40+) | `av1_amf` (RX 7000+) | `av1_qsv` (Arc+) |

> GPU encoders are **auto-detected** at startup. Only encoders supported by your hardware and FFmpeg build will appear in the codec dropdown.

---

## Building from Source (for Developers)

### Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.12.x |
| pip | Latest |
| FFmpeg | 8.x (on PATH) |

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
python build.py
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
│   │   ├── encoder.py          # FFmpeg worker thread
│   │   └── gpu_detect.py       # GPU encoder auto-detection
│   └── ui/
│       ├── main_window.py      # Main application window
│       ├── terminal_widget.py  # Embedded terminal output
│       ├── help_dialogs.py     # Help dialog windows
│       └── themes.py           # Light and dark theme stylesheets
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
| No GPU encoders in dropdown | Update GPU drivers. Use the **full build** of FFmpeg. Verify your GPU supports the encoder. |
| GPU encoding fails | Update GPU drivers. Check NVIDIA/AMD/Intel driver versions. Try a different GPU preset. |

---

## License

MIT License — free for personal and commercial use.

---

## Version History

- **v1.2** — Drag & drop file import, preset profiles (save/load/delete encoding settings), video trimming (start/end time), output format selection with codec-aware filtering (14 containers), concatenate/merge multiple files, batch progress bar, scroll-safe combo boxes, application icon on title bar and taskbar
- **v1.1.1** — Fixed audio/subtitle dropdowns being editable, fixed OS dark theme interfering with app themes
- **v1.1** — GPU-accelerated encoding (NVIDIA NVENC, AMD AMF, Intel QSV) with parallel auto-detection, smart pixel format filtering per encoder, comprehensive help text with parameter tables, faster startup via parallel GPU probing
- **v1.0.3** — Added GPU-accelerated encoding (NVIDIA NVENC, AMD AMF, Intel QSV) with auto-detection, GPU Encoding Guide in Help menu, hardware-accelerated decoding
- **v1.0.2a** — Fixed encoding failure in target bitrate mode (SVT-AV1 VBR), fixed app crash after encoding completes, fixed dark theme white widgets, fixed arrow visibility in themed spinboxes & comboboxes, added dark/light theme toggle in Settings menu
- **v1.0.2** — Added FPS control (11 presets + custom), video bitrate selector (256K–20M), app icon, fixed window closing during batch processing
- **v1.0.1** — Added H.266/VVC codec, AV1 encoder comparison guide, FFmpeg 8.x support, auto-detection of FFmpeg in winget/common paths
- **v1.0.0** — Initial release with full GUI, 7 codecs, batch processing, resolution presets, and standalone EXE
