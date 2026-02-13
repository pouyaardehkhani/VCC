"""
Help dialogs for VCC - Codec info and Pixel Format info.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTextBrowser, QPushButton, QHBoxLayout,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

from vcc.core.codecs import CODEC_HELP_TEXT, AUDIO_HELP_TEXT
from vcc.core.pixel_formats import PIXEL_FORMAT_HELP_TEXT

FPS_HELP_TEXT = """\
<h2>Frame Rate (FPS) Guide</h2>

<p>Frame rate (Frames Per Second) determines how many individual images are displayed each second.
A higher FPS results in smoother motion but increases file size and encoding time.</p>

<hr>

<h3>Available Presets</h3>
<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">
<tr><th>FPS</th><th>Name</th><th>Use Case</th><th>Notes</th></tr>
<tr><td><b>12</b></td><td>Low Animation</td><td>Simple animation, stop-motion</td>
    <td>Traditional hand-drawn animation rate. Very choppy for live-action.
    Minimal data &mdash; extremely small files.</td></tr>
<tr><td><b>15</b></td><td>Low</td><td>Security cameras, old webcams, screencasts</td>
    <td>Noticeably choppy on moving content. Acceptable for surveillance
    or static-heavy recordings.</td></tr>
<tr><td><b>18</b></td><td>Low&ndash;Medium</td><td>Early silent film era, low-bandwidth video</td>
    <td>Uncommon today. Slightly smoother than 15 fps. Can be used to
    save space when minimal motion is involved.</td></tr>
<tr><td><b>20</b></td><td>Medium&ndash;Low</td><td>Old video games, retro content, low-bandwidth streams</td>
    <td>Below modern standards but playable. Often used for animated GIF
    creation or resource-constrained devices.</td></tr>
<tr><td><b>23.976</b></td><td>Film (NTSC)</td><td>Cinema, Blu-ray, streaming movies</td>
    <td>The standard cinema frame rate (often written as &ldquo;24 fps&rdquo;).
    Gives a classic cinematic feel. Used by virtually all Hollywood films
    and most streaming services for movie content.</td></tr>
<tr><td><b>24</b></td><td>Film</td><td>Cinema, artistic videography</td>
    <td>True 24 fps &mdash; virtually identical to 23.976 for most purposes.
    Preferred when exact integer frame rate is needed (e.g., some web players).</td></tr>
<tr><td><b>25</b></td><td>PAL</td><td>European TV broadcast (PAL / SECAM regions)</td>
    <td>Standard frame rate for Europe, Australia, and parts of Asia &amp; Africa.
    Matches the 50 Hz mains frequency in those regions.</td></tr>
<tr><td><b>29.97</b></td><td>NTSC</td><td>North American &amp; Japanese TV broadcast</td>
    <td>Standard NTSC broadcast rate. Often called &ldquo;30 fps&rdquo; informally.
    Required for broadcast compatibility in NTSC regions.</td></tr>
<tr><td><b>30</b></td><td>Standard</td><td>Online video, webcams, general-purpose recording</td>
    <td>The most common frame rate for web content and social media.
    Good balance between smoothness and file size. Universally supported.</td></tr>
<tr><td><b>50</b></td><td>PAL High</td><td>European sports, high-motion PAL content</td>
    <td>Double the PAL rate. Captures fast action with smooth motion.
    Used for sports broadcasts in PAL regions and for slow-motion
    playback at 25 fps (2&times; slow-mo).</td></tr>
<tr><td><b>60</b></td><td>Smooth</td><td>Gaming, sports, action content, streaming</td>
    <td>Very smooth motion. Popular for gaming videos, live streams,
    and action-heavy content. Significantly larger files than 30 fps.</td></tr>
</table>

<hr>

<h3>Custom Frame Rate</h3>
<p>Select <b>Custom</b> from the dropdown to enter any value between 1 and 300 fps.
This is useful for uncommon frame rates such as:</p>
<ul>
<li><b>48 fps</b> &mdash; High-frame-rate cinema (e.g., <i>The Hobbit</i>).</li>
<li><b>59.94 fps</b> &mdash; NTSC double rate for broadcast sports.</li>
<li><b>120 fps</b> &mdash; Slow-motion source or high-end gaming capture.</li>
<li><b>144 fps</b> &mdash; Matching 144 Hz gaming monitors.</li>
<li><b>240 fps</b> &mdash; Super slow-motion analysis and sports replays.</li>
<li>Any fractional rate your workflow requires.</li>
</ul>

<hr>

<h3>How FPS Affects File Size</h3>
<p>Doubling the frame rate roughly doubles the data the encoder must process, though smart
codecs reuse similar frames. As a rule of thumb:</p>
<ul>
<li>24 fps &rarr; 30 fps &asymp; +25% file size</li>
<li>30 fps &rarr; 60 fps &asymp; +50&ndash;80% file size</li>
<li>60 fps &rarr; 120 fps &asymp; +60&ndash;90% file size</li>
</ul>

<h3>FPS Conversion Considerations</h3>
<ul>
<li><b>Reducing FPS</b> (e.g., 60&rarr;30): Drops frames. Can cause slight judder if source has
    fast motion. Good for saving space.</li>
<li><b>Increasing FPS</b> (e.g., 24&rarr;60): FFmpeg duplicates or blends frames. Does <i>not</i>
    create real new motion data. May look unnatural without AI interpolation.</li>
<li><b>Matching source FPS</b>: Leave FPS as &ldquo;Default&rdquo; to keep the original frame rate
    &mdash; this is usually the best choice unless you have a specific requirement.</li>
</ul>

<h3>Recommendations</h3>
<p><b>General content:</b> Keep original FPS (Default) or use 30 fps.<br>
<b>Cinematic look:</b> 23.976 or 24 fps.<br>
<b>Gaming / action:</b> 60 fps for smooth playback.<br>
<b>Slow-motion source:</b> Use Custom to enter 120+ fps, then play back at 24/30 fps.<br>
<b>Smallest files:</b> 24 fps (fewer frames = less data).</p>
"""

BITRATE_HELP_TEXT = """\
<h2>Video Bitrate Guide</h2>

<p>Bitrate is the amount of data used per second of video. Higher bitrate means better quality
but larger file sizes. When a bitrate is set, it overrides quality-based encoding (CRF/CQ) and
uses <b>target bitrate mode</b> instead.</p>

<hr>

<h3>Available Presets</h3>
<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">
<tr><th>Bitrate</th><th>Quality Level</th><th>Typical Use Case</th><th>Est. File Size (1 hr)</th></tr>
<tr><td><b>256K</b></td><td>Very Low</td>
    <td>Extremely low-bandwidth streaming, audio-heavy content with minimal video motion</td>
    <td>&asymp; 110 MB</td></tr>
<tr><td><b>384K</b></td><td>Low</td>
    <td>Mobile streaming on slow connections, video calls, small-window playback</td>
    <td>&asymp; 165 MB</td></tr>
<tr><td><b>512K</b></td><td>Low&ndash;Medium</td>
    <td>Low-resolution web video (360p/480p), background monitoring</td>
    <td>&asymp; 220 MB</td></tr>
<tr><td><b>768K</b></td><td>Medium&ndash;Low</td>
    <td>480p streaming, mobile video, podcasts with camera</td>
    <td>&asymp; 330 MB</td></tr>
<tr><td><b>1M</b> (1 Mbps)</td><td>Medium</td>
    <td>SD video (480p), video conferencing, low-end 720p</td>
    <td>&asymp; 430 MB</td></tr>
<tr><td><b>1.5M</b></td><td>Medium&ndash;Good</td>
    <td>720p with modern codecs (AV1/HEVC), web content, social media</td>
    <td>&asymp; 650 MB</td></tr>
<tr><td><b>2M</b></td><td>Good</td>
    <td>720p standard, 1080p with efficient codecs (AV1/HEVC), YouTube SD</td>
    <td>&asymp; 860 MB</td></tr>
<tr><td><b>5M</b></td><td>High</td>
    <td>1080p streaming (Netflix-like), 720p high quality, YouTube HD</td>
    <td>&asymp; 2.1 GB</td></tr>
<tr><td><b>10M</b></td><td>Very High</td>
    <td>1080p premium quality, 4K with efficient codec, Blu-ray level</td>
    <td>&asymp; 4.3 GB</td></tr>
<tr><td><b>15M</b></td><td>Excellent</td>
    <td>4K streaming, high-quality 1080p archival, professional web delivery</td>
    <td>&asymp; 6.4 GB</td></tr>
<tr><td><b>20M</b></td><td>Premium</td>
    <td>4K high quality, professional video, broadcast-grade content</td>
    <td>&asymp; 8.6 GB</td></tr>
</table>

<hr>

<h3>Bitrate Mode vs CRF Mode</h3>
<ul>
<li><b>Default (no bitrate set)</b>: The encoder uses <b>CRF / Constant Quality</b> mode. FFmpeg
    adjusts the bitrate dynamically to maintain consistent visual quality. This is generally
    recommended for single-pass offline encoding.</li>
<li><b>Target Bitrate mode</b>: When you select a specific bitrate, the encoder aims for that
    exact data rate. Quality may vary scene-to-scene, but the file size is more predictable.
    This is common for streaming and bandwidth-constrained scenarios.</li>
</ul>

<h3>Bitrate vs Resolution Guidelines</h3>
<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">
<tr><th>Resolution</th><th>Codec</th><th>Suggested Range</th></tr>
<tr><td>480p</td><td>H.264</td><td>500K &ndash; 2M</td></tr>
<tr><td>720p</td><td>H.264</td><td>1.5M &ndash; 5M</td></tr>
<tr><td>1080p</td><td>H.264</td><td>3M &ndash; 10M</td></tr>
<tr><td>4K</td><td>H.264</td><td>10M &ndash; 20M+</td></tr>
<tr><td>480p</td><td>HEVC/AV1</td><td>256K &ndash; 1M</td></tr>
<tr><td>720p</td><td>HEVC/AV1</td><td>768K &ndash; 2M</td></tr>
<tr><td>1080p</td><td>HEVC/AV1</td><td>1.5M &ndash; 5M</td></tr>
<tr><td>4K</td><td>HEVC/AV1</td><td>5M &ndash; 15M</td></tr>
</table>

<h3>Recommendations</h3>
<p><b>Best quality at any size:</b> Leave as Default (CRF mode) and adjust the CRF value instead.<br>
<b>Predictable file size:</b> Choose a bitrate preset matching your resolution and codec.<br>
<b>Streaming / upload:</b> Match the target platform&rsquo;s recommended bitrate.<br>
<b>Archival:</b> Use Default (CRF) with a low CRF value for consistent quality.</p>
"""

RESOLUTION_HELP_TEXT = """\
<h2>Video Resolutions Guide</h2>

<p>Resolution is the number of pixels in each dimension (Width &times; Height).
Higher resolution = more detail but larger files and longer encoding times.</p>

<hr>

<h3>Common Resolutions</h3>
<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">
<tr><th>Name</th><th>Width</th><th>Height</th><th>Aspect Ratio</th><th>Notes</th></tr>
<tr><td><b>8K UHD</b></td><td>7680</td><td>4320</td><td>16:9</td>
    <td>Ultra-high-end. Massive files. Very few displays support it.</td></tr>
<tr><td><b>4K UHD</b></td><td>3840</td><td>2160</td><td>16:9</td>
    <td>Standard 4K. Excellent detail. Common on modern TVs and monitors.</td></tr>
<tr><td><b>4K DCI</b></td><td>4096</td><td>2160</td><td>~1.9:1</td>
    <td>Cinema 4K. Slightly wider than UHD. Used in film production.</td></tr>
<tr><td><b>1440p (QHD)</b></td><td>2560</td><td>1440</td><td>16:9</td>
    <td>Quad HD. Popular for gaming monitors. Good middle ground.</td></tr>
<tr><td><b>1080p (Full HD)</b></td><td>1920</td><td>1080</td><td>16:9</td>
    <td>The standard for most content. Great balance of quality and size.</td></tr>
<tr><td><b>720p (HD)</b></td><td>1280</td><td>720</td><td>16:9</td>
    <td>HD ready. Good for saving space while keeping decent quality.</td></tr>
<tr><td><b>480p (SD)</b></td><td>854</td><td>480</td><td>~16:9</td>
    <td>Standard definition. Small files. Acceptable on small screens.</td></tr>
<tr><td><b>480p (4:3)</b></td><td>640</td><td>480</td><td>4:3</td>
    <td>Classic 4:3 SD. Old TV / VGA standard.</td></tr>
<tr><td><b>360p</b></td><td>640</td><td>360</td><td>16:9</td>
    <td>Low quality. Used for previews or very low bandwidth.</td></tr>
<tr><td><b>240p</b></td><td>426</td><td>240</td><td>~16:9</td>
    <td>Very low quality. Tiny files. Mobile on slow connections.</td></tr>
</table>

<hr>

<h3>Ultrawide Resolutions</h3>
<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">
<tr><th>Name</th><th>Width</th><th>Height</th><th>Aspect Ratio</th></tr>
<tr><td><b>UWQHD</b></td><td>3440</td><td>1440</td><td>21:9</td></tr>
<tr><td><b>UWHD</b></td><td>2560</td><td>1080</td><td>21:9</td></tr>
<tr><td><b>Super Ultrawide</b></td><td>5120</td><td>1440</td><td>32:9</td></tr>
</table>

<hr>

<h3>Vertical / Portrait (Mobile)</h3>
<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">
<tr><th>Name</th><th>Width</th><th>Height</th><th>Use Case</th></tr>
<tr><td><b>1080×1920</b></td><td>1080</td><td>1920</td><td>Instagram/TikTok Reels, Stories</td></tr>
<tr><td><b>720×1280</b></td><td>720</td><td>1280</td><td>Mobile vertical video</td></tr>
<tr><td><b>1080×1080</b></td><td>1080</td><td>1080</td><td>Instagram square posts</td></tr>
</table>

<hr>

<h3>How Resolution Affects File Size</h3>
<p>Doubling both width and height means <b>4&times; the pixels</b> and roughly 4&times; the file size
(at the same quality settings). For example:</p>
<ul>
<li>720p (921,600 pixels) &rarr; 1080p (2,073,600 pixels) = ~2.25&times; more pixels</li>
<li>1080p (2,073,600 pixels) &rarr; 4K (8,294,400 pixels) = ~4&times; more pixels</li>
</ul>

<h3>Recommendations</h3>
<p><b>Archiving / high quality:</b> Keep original resolution, or use 1080p/4K.<br>
<b>Saving disk space:</b> 720p offers significant savings with acceptable quality.<br>
<b>Sharing online:</b> 1080p is the sweet spot &mdash; universally supported and looks great.<br>
<b>Very small files:</b> 480p for mobile or slow networks.<br>
<b>Tip:</b> Always maintain the original aspect ratio to avoid stretching or black bars.</p>
"""


class HelpDialog(QDialog):
    """Scrollable HTML help dialog."""

    def __init__(self, title: str, html_content: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(QSize(700, 550))
        self.resize(780, 620)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(html_content)
        font = QFont("Segoe UI", 10)
        browser.setFont(font)
        browser.setStyleSheet("""
            QTextBrowser {
                background-color: #fafafa;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        layout.addWidget(browser)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)


class CodecHelpDialog(HelpDialog):
    def __init__(self, parent=None):
        super().__init__("Codec Information", CODEC_HELP_TEXT, parent)


class PixelFormatHelpDialog(HelpDialog):
    def __init__(self, parent=None):
        super().__init__("Pixel Format Information", PIXEL_FORMAT_HELP_TEXT, parent)


class AudioHelpDialog(HelpDialog):
    def __init__(self, parent=None):
        super().__init__("Audio Codec Information", AUDIO_HELP_TEXT, parent)


class ResolutionHelpDialog(HelpDialog):
    def __init__(self, parent=None):
        super().__init__("Resolution Guide", RESOLUTION_HELP_TEXT, parent)


class FPSHelpDialog(HelpDialog):
    def __init__(self, parent=None):
        super().__init__("Frame Rate (FPS) Guide", FPS_HELP_TEXT, parent)


class BitrateHelpDialog(HelpDialog):
    def __init__(self, parent=None):
        super().__init__("Video Bitrate Guide", BITRATE_HELP_TEXT, parent)


GPU_ENCODING_HELP_TEXT = """\
<h2>GPU-Accelerated Encoding Guide</h2>

<p>VCC can use your graphics card (GPU) for hardware-accelerated video encoding,
which is typically <b>10&ndash;50&times; faster</b> than CPU-based software encoding
with near-zero CPU usage.</p>

<hr>

<h3>How It Works</h3>
<p>Modern GPUs contain a dedicated hardware encoder (a fixed-function ASIC) that is
separate from the GPU's shader cores. This means encoding doesn't affect gaming or
other GPU workloads, and your CPU is free for other tasks.</p>
<p>VCC <b>auto-detects</b> your GPU's encoding capabilities at startup by running a
real hardware test. Only encoders that actually work on your system appear in the
Codec dropdown (marked with &#x1F3AE;).</p>

<hr>

<h3>Supported GPU Vendors &amp; Hardware Requirements</h3>
<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">
<tr><th>Vendor</th><th>Technology</th><th>H.264</th><th>H.265/HEVC</th><th>AV1</th></tr>
<tr><td><b>NVIDIA</b></td><td>NVENC</td>
    <td>GeForce GTX 600+<br>Kepler or newer</td>
    <td>GeForce GTX 900+<br>Maxwell 2nd gen+</td>
    <td>RTX 4000+ only<br>Ada Lovelace</td></tr>
<tr><td><b>AMD</b></td><td>AMF (VCE/VCN)</td>
    <td>HD 7000+ (GCN 1.0+)</td>
    <td>R9 285+ (GCN 3.0+)</td>
    <td>RX 7000+ (RDNA 3)</td></tr>
<tr><td><b>Intel</b></td><td>Quick Sync (QSV)</td>
    <td>2nd Gen+ (Sandy Bridge)</td>
    <td>6th Gen+ (Skylake)</td>
    <td>Arc A-series / 12th Gen+</td></tr>
</table>
<p><b>Note:</b> Your FFmpeg build must include the GPU encoder libraries. The &ldquo;full&rdquo;
build from Gyan.dev or BtbN includes all of them.</p>

<hr>

<h3>GPU vs CPU Encoding &mdash; When to Use Which</h3>
<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">
<tr><th>Aspect</th><th>GPU Encoding</th><th>CPU Encoding</th></tr>
<tr><td><b>Encoding Speed</b></td>
    <td>&#x1F7E2; Very Fast (10&ndash;50&times; faster)</td>
    <td>&#x1F534; Slow</td></tr>
<tr><td><b>Quality per Bitrate</b></td>
    <td>&#x1F7E1; Good (5&ndash;15% behind CPU at same bitrate)</td>
    <td>&#x1F7E2; Best</td></tr>
<tr><td><b>CPU Usage</b></td>
    <td>&#x1F7E2; Near zero (GPU does the work)</td>
    <td>&#x1F534; 100% (all cores)</td></tr>
<tr><td><b>Power Efficiency</b></td>
    <td>&#x1F7E2; Very efficient (dedicated ASIC)</td>
    <td>&#x1F7E1; Higher power draw</td></tr>
<tr><td><b>Availability</b></td>
    <td>&#x1F7E1; Requires compatible GPU + drivers</td>
    <td>&#x1F7E2; Always available</td></tr>
</table>

<h4>&#x2705; Use GPU encoding when:</h4>
<ul>
<li><b>Batch processing</b> &mdash; Many files where speed matters most.</li>
<li><b>Quick previews</b> &mdash; Fast draft before a final CPU render.</li>
<li><b>Streaming / recording</b> &mdash; Real-time encoding with minimal latency.</li>
<li><b>Multitasking</b> &mdash; Keep your CPU free for other work.</li>
<li><b>Large files (4K/8K)</b> &mdash; GPU encoding scales better with resolution.</li>
</ul>

<h4>&#x1F3AF; Use CPU encoding when:</h4>
<ul>
<li><b>Maximum quality</b> &mdash; CPU encoders achieve ~5&ndash;15% better quality/bitrate.</li>
<li><b>Archival</b> &mdash; File size and quality matter more than speed.</li>
<li><b>AV1 is needed</b> &mdash; SVT-AV1 (CPU) still provides the best AV1 quality.</li>
<li><b>No compatible GPU</b> &mdash; CPU encoding is always available.</li>
</ul>

<hr>

<h3>Detailed Parameters by Vendor</h3>

<h4>&#x1F7E2; NVIDIA NVENC</h4>
<p>Best GPU encoder quality since Turing (RTX 20-series). RTX 30/40-series NVENC
approaches CPU encoder quality.</p>
<table border="1" cellpadding="5" cellspacing="0" style="border-collapse:collapse;">
<tr><th>Parameter</th><th>Range</th><th>Default</th><th>Recommended</th><th>Description</th></tr>
<tr><td><b>Preset</b></td><td>p1 &ndash; p7</td><td>p4</td><td>p4 &ndash; p5</td>
    <td><b>p1</b> = fastest encoding, lowest quality.<br>
    <b>p7</b> = slowest encoding, best quality.<br>
    <b>p4</b> is the sweet spot for most users.<br>
    p6&ndash;p7 are good for archival.</td></tr>
<tr><td><b>CQ (Quality)</b></td><td>0 &ndash; 51</td><td>28</td><td>24 &ndash; 30</td>
    <td>Constant Quality &mdash; NVENC's equivalent of CRF.<br>
    <b>0</b> = highest quality (near-lossless).<br>
    <b>51</b> = lowest quality, smallest file.<br>
    Visually transparent: ~20&ndash;25.</td></tr>
</table>
<p><b>Bit depth:</b></p>
<ul>
<li><b>H.264 NVENC:</b> 8-bit only. 10-bit pixel formats are hidden.</li>
<li><b>H.265 NVENC:</b> 8-bit and 10-bit. Use <code>yuv420p10le</code> for best quality
    (FFmpeg auto-converts to <code>p010le</code> internally).</li>
<li><b>AV1 NVENC:</b> 8-bit and 10-bit. Requires RTX 4000+ (Ada Lovelace).</li>
</ul>

<h4>&#x1F534; AMD AMF</h4>
<p>Quality improved significantly with RDNA 2+ (RX 6000+). AV1 encoding requires
RDNA 3 (RX 7000+).</p>
<table border="1" cellpadding="5" cellspacing="0" style="border-collapse:collapse;">
<tr><th>Parameter</th><th>Range</th><th>Default</th><th>Recommended</th><th>Description</th></tr>
<tr><td><b>Preset</b></td><td>speed / balanced / quality</td><td>balanced</td><td>balanced / quality</td>
    <td><b>speed</b> = fastest, lowest quality.<br>
    <b>balanced</b> = good trade-off.<br>
    <b>quality</b> = best quality, slower.<br>
    AV1 AMF also has <b>high_quality</b>.</td></tr>
<tr><td><b>QP (Quality)</b></td><td>0 &ndash; 51</td><td>26&ndash;28</td><td>22 &ndash; 30</td>
    <td>Quantization Parameter.<br>
    <b>0</b> = highest quality.<br>
    <b>51</b> = lowest quality.<br>
    VCC automatically sets both QP_I and QP_P to the same value.</td></tr>
</table>
<p><b>Bit depth:</b> H.264 AMF = 8-bit only. H.265/AV1 AMF = 8-bit and 10-bit.</p>

<h4>&#x1F535; Intel Quick Sync (QSV)</h4>
<p>Available on Intel CPUs with integrated graphics. Quality varies by generation;
11th Gen+ (Tiger Lake) and Arc GPUs offer competitive quality.</p>
<table border="1" cellpadding="5" cellspacing="0" style="border-collapse:collapse;">
<tr><th>Parameter</th><th>Range</th><th>Default</th><th>Recommended</th><th>Description</th></tr>
<tr><td><b>Preset</b></td><td>veryfast &ndash; veryslow</td><td>medium</td><td>medium / slow</td>
    <td>Same preset names as x264/x265.<br>
    <b>veryfast</b> = fastest, lowest quality.<br>
    <b>veryslow</b> = slowest, best quality.</td></tr>
<tr><td><b>Global Quality</b></td><td>1 &ndash; 51</td><td>25&ndash;28</td><td>22 &ndash; 30</td>
    <td>Intel's equivalent of CRF.<br>
    <b>1</b> = highest quality.<br>
    <b>51</b> = lowest quality.</td></tr>
</table>
<p><b>Bit depth:</b> H.264 QSV = 8-bit only. H.265/AV1 QSV = 8-bit and 10-bit.</p>
<p><b>Note:</b> QSV requires Intel integrated graphics to be enabled in BIOS. On laptops
with both Intel and NVIDIA GPUs, you can often use both NVENC and QSV.</p>

<hr>

<h3>Pixel Format Compatibility</h3>
<p>VCC <b>automatically filters</b> the pixel format dropdown so you can only
select formats your chosen encoder supports. Key rules:</p>
<ul>
<li><b>H.264 (all GPU vendors):</b> 8-bit only &mdash; 10-bit options are hidden.</li>
<li><b>H.265 / AV1 (all GPU vendors):</b> 8-bit and 10-bit &mdash; use <code>yuv420p10le</code>
    for best quality. FFmpeg transparently converts format names for you.</li>
</ul>
<p><b>For GPU encoding, <code>yuv420p</code> always works.</b> For H.265/AV1 GPU,
<code>yuv420p10le</code> is recommended for reduced banding and better compression.</p>

<hr>

<h3>Bitrate Mode with GPU Encoders</h3>
<p>GPU encoders support target bitrate mode just like CPU encoders. When a bitrate
is set in VCC, the quality parameter (CQ/QP/Global Quality) is ignored and the
encoder targets the specified bitrate instead. VCC automatically configures the
rate control mode for each vendor:</p>
<ul>
<li><b>NVIDIA:</b> VBR (variable bitrate) with maxrate/bufsize matching the target.</li>
<li><b>AMD:</b> VBR Peak with maxrate/bufsize.</li>
<li><b>Intel:</b> Standard bitrate targeting.</li>
</ul>

<hr>

<h3>Troubleshooting</h3>
<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">
<tr><th>Problem</th><th>Solution</th></tr>
<tr><td>No GPU encoders in dropdown</td>
    <td>Install the <b>full build</b> of FFmpeg (not &ldquo;essentials&rdquo;).
    Update GPU drivers to the latest version.</td></tr>
<tr><td>Encoding fails with GPU encoder</td>
    <td>Update GPU drivers. Ensure your GPU model supports that codec
    (e.g. AV1 NVENC requires RTX 4000+).</td></tr>
<tr><td>NVENC &ldquo;too many sessions&rdquo;</td>
    <td>Consumer NVIDIA GPUs allow 3&ndash;5 simultaneous NVENC sessions.
    Close other encoding/streaming apps (OBS, Discord, etc.).</td></tr>
<tr><td>QSV not detected</td>
    <td>Enable Intel integrated graphics in BIOS. Install Intel
    Media SDK / oneVPL drivers. Some desktop CPUs with &ldquo;F&rdquo;
    suffix (e.g. i7-12700F) lack integrated graphics.</td></tr>
<tr><td>Low quality output</td>
    <td>Lower the CQ/QP value (e.g. 20&ndash;25) or increase bitrate.
    Use a slower preset (p5&ndash;p7 for NVENC).</td></tr>
<tr><td>Encoder detected but fails on specific file</td>
    <td>Some source files use features the GPU encoder can't handle.
    Try a different pixel format or fall back to CPU encoding.</td></tr>
</table>

<hr>

<h3>Quick Recommendations</h3>
<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">
<tr><th>Goal</th><th>GPU Encoder</th><th>Settings</th></tr>
<tr><td><b>Fastest possible</b></td><td>H.264 NVENC</td>
    <td>Preset p1&ndash;p3, CQ 28&ndash;32, yuv420p</td></tr>
<tr><td><b>Best GPU quality</b></td><td>HEVC NVENC</td>
    <td>Preset p5&ndash;p7, CQ 22&ndash;26, yuv420p10le</td></tr>
<tr><td><b>Fast + smaller files</b></td><td>HEVC NVENC</td>
    <td>Preset p4, CQ 26&ndash;30, yuv420p10le</td></tr>
<tr><td><b>Most compatible GPU output</b></td><td>H.264 NVENC/QSV</td>
    <td>Preset p4/medium, CQ 24&ndash;28, yuv420p</td></tr>
</table>
"""


class GPUEncodingHelpDialog(HelpDialog):
    def __init__(self, parent=None):
        super().__init__("GPU Encoding Guide", GPU_ENCODING_HELP_TEXT, parent)


OUTPUT_FORMAT_HELP_TEXT = """\
<h2>Output Format (Container) Guide</h2>

<p>The <b>output format</b> (also called <em>container</em>) determines the file
wrapper around your video, audio, and subtitle streams. Different containers
support different codecs and features.</p>

<hr>

<h3>Available Formats</h3>
<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">
<tr><th>Format</th><th>Extension</th><th>Best For</th><th>Video Codecs</th><th>Audio Codecs</th><th>Subtitles</th></tr>
<tr><td><b>Auto</b></td><td>(same as source)</td><td>Default &mdash; keeps the original container</td>
    <td>Any</td><td>Any</td><td>Any</td></tr>
<tr><td><b>MKV</b></td><td>.mkv</td><td>Archival, multi-track, universal codec support</td>
    <td>All codecs (H.264, H.265, AV1, VP9, etc.)</td>
    <td>All (AAC, FLAC, Opus, AC3, DTS, etc.)</td>
    <td>&#x2705; SRT, ASS/SSA, PGS, VobSub</td></tr>
<tr><td><b>MP4</b></td><td>.mp4</td><td>Maximum compatibility, streaming, web, mobile</td>
    <td>H.264, H.265, AV1, MPEG-4</td>
    <td>AAC, MP3, AC3, Opus (limited)</td>
    <td>&#x26A0; mov_text only (basic)</td></tr>
<tr><td><b>WebM</b></td><td>.webm</td><td>Web video, HTML5 &lt;video&gt;</td>
    <td>VP9, AV1 (VP8 legacy)</td>
    <td>Opus, Vorbis</td>
    <td>&#x2705; WebVTT</td></tr>
<tr><td><b>AVI</b></td><td>.avi</td><td>Legacy compatibility, older devices</td>
    <td>MPEG-4, H.264 (limited)</td>
    <td>MP3, PCM, AC3</td>
    <td>&#x274C; Not recommended</td></tr>
<tr><td><b>MOV</b></td><td>.mov</td><td>Apple ecosystem, Final Cut Pro, ProRes</td>
    <td>H.264, H.265, ProRes, MPEG-4</td>
    <td>AAC, ALAC, PCM, AC3</td>
    <td>&#x26A0; mov_text</td></tr>
<tr><td><b>TS</b></td><td>.ts</td><td>Broadcast, IPTV, live streaming</td>
    <td>H.264, H.265, MPEG-2</td>
    <td>AAC, AC3, MP2</td>
    <td>&#x2705; DVB subtitles</td></tr>
<tr><td><b>FLV</b></td><td>.flv</td><td>Flash-era streaming (legacy)</td>
    <td>H.264, VP6 (legacy)</td>
    <td>AAC, MP3</td>
    <td>&#x274C; None</td></tr>
<tr><td><b>WMV</b></td><td>.wmv</td><td>Windows Media, older Windows apps</td>
    <td>WMV, VC-1 (H.264 via ASF)</td>
    <td>WMA, MP3</td>
    <td>&#x274C; Not recommended</td></tr>
<tr><td><b>OGG</b></td><td>.ogg</td><td>Open-source, Theora video, Vorbis audio</td>
    <td>Theora (VP8 limited)</td>
    <td>Vorbis, Opus</td>
    <td>&#x274C; None</td></tr>
<tr><td><b>M4V</b></td><td>.m4v</td><td>iTunes, Apple TV, DRM content</td>
    <td>H.264, H.265</td>
    <td>AAC, AC3</td>
    <td>&#x26A0; mov_text</td></tr>
<tr><td><b>MPG</b></td><td>.mpg</td><td>DVD, legacy MPEG-1/2 content</td>
    <td>MPEG-1, MPEG-2</td>
    <td>MP2, AC3</td>
    <td>&#x274C; Not recommended</td></tr>
<tr><td><b>3GP</b></td><td>.3gp</td><td>Mobile phones (legacy, small screens)</td>
    <td>H.263, H.264, MPEG-4</td>
    <td>AAC, AMR</td>
    <td>&#x274C; None</td></tr>
<tr><td><b>MXF</b></td><td>.mxf</td><td>Professional broadcast, post-production</td>
    <td>MPEG-2, H.264, DNxHD, ProRes</td>
    <td>PCM, AAC</td>
    <td>&#x274C; None</td></tr>
</table>

<hr>

<h3>Choosing the Right Format</h3>
<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">
<tr><th>Goal</th><th>Recommended Format</th><th>Why</th></tr>
<tr><td><b>Maximum compatibility</b></td><td>MP4</td>
    <td>Plays on virtually every device, OS, and browser.</td></tr>
<tr><td><b>Maximum flexibility</b></td><td>MKV</td>
    <td>Supports every codec, multiple audio/subtitle tracks, chapters.</td></tr>
<tr><td><b>Web embedding</b></td><td>WebM or MP4</td>
    <td>WebM for VP9/AV1, MP4 for H.264/H.265. Both work in HTML5.</td></tr>
<tr><td><b>Archival / lossless</b></td><td>MKV</td>
    <td>Supports lossless codecs (FFV1, FLAC) and all metadata.</td></tr>
<tr><td><b>Apple devices</b></td><td>MOV or MP4</td>
    <td>Native support on macOS, iOS, Apple TV.</td></tr>
<tr><td><b>Streaming / broadcast</b></td><td>TS</td>
    <td>Designed for streaming; resilient to transmission errors.</td></tr>
<tr><td><b>Professional editing</b></td><td>MXF or MOV</td>
    <td>Industry-standard for broadcast and NLE workflows.</td></tr>
</table>

<hr>

<h3>Format &amp; Codec Compatibility Notes</h3>
<ul>
<li><b>MKV</b> accepts virtually any codec combination. If in doubt, use MKV.</li>
<li><b>MP4</b> does <b>not</b> support VP9, Theora, FLAC, or Vorbis audio.</li>
<li><b>WebM</b> only supports VP8/VP9/AV1 video and Opus/Vorbis audio.</li>
<li><b>AVI</b> has poor support for modern codecs (H.265, AV1) and advanced features.</li>
<li>When using <b>Auto</b>, the output keeps the same container as the source file.</li>
<li>If the chosen codec is incompatible with the selected container, FFmpeg will
    report an error &mdash; switch to MKV for guaranteed compatibility.</li>
</ul>

<hr>

<h3>Subtitles &amp; Container Support</h3>
<p>Not all containers support subtitle streams:</p>
<ul>
<li><b>MKV:</b> Full subtitle support (SRT, ASS/SSA, PGS, VobSub, etc.)</li>
<li><b>MP4/MOV/M4V:</b> Only <code>mov_text</code> (basic text subtitles). Other formats will fail.</li>
<li><b>WebM:</b> WebVTT subtitles only.</li>
<li><b>TS:</b> DVB-format subtitles (bitmap-based).</li>
<li><b>AVI/FLV/WMV/OGG/3GP/MXF:</b> No reliable subtitle support.</li>
</ul>
<p><b>Tip:</b> If you need subtitles, use <b>MKV</b> or set subtitle mode to
&ldquo;Remove&rdquo; for containers that don't support them.</p>
"""


class OutputFormatHelpDialog(HelpDialog):
    def __init__(self, parent=None):
        super().__init__("Output Format Guide", OUTPUT_FORMAT_HELP_TEXT, parent)


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Video Codec Converter")
        self.setFixedSize(420, 260)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(False)
        browser.setHtml("""
        <div style="text-align:center;">
        <h2>Video Codec Converter (VCC)</h2>
        <p>Version 1.2</p>
        <p>A graphical FFmpeg front-end for batch video transcoding.</p>
        <hr>
        <p style="color:#666;">Powered by FFmpeg<br>
        Built with Python &amp; PyQt6</p>
        </div>
        """)
        browser.setStyleSheet("QTextBrowser { border: none; background: transparent; }")
        layout.addWidget(browser)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
