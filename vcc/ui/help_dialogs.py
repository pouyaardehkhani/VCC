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
        <p>Version 1.0.2a</p>
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
