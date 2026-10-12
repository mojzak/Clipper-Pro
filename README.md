# 🎬 Clipper Pro • Twitch & Kick Batch Downloader & Converter

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![Gradio](https://img.shields.io/badge/Gradio-6.0-orange?logo=gradio&logoColor=white)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Optimized-green?logo=ffmpeg&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-purple)
![Cost](https://img.shields.io/badge/Cloud%20Hosting-0%20DHS%20%2F%20Free-success)

**A high-performance Full Stack application to batch download clips and VODs from Twitch & Kick, with smart automated conversion into Mobile Reels (9:16) or PC Landscape (16:9).**

[Features](#-key-features) • [Quick Start](#-quick-start-local) • [Formats](#-output-video-formats) • [CLI Mode](#-cli-usage) • [Free Cloud Deployment](#-free-cloud-deployment-0-dhs)

</div>

---

## 🌟 Key Features

- ⚡ **Multi-Platform Native Support**: Seamlessly extracts high-quality clips and VODs from both **Twitch** (`clips.twitch.tv`, `twitch.tv/.../clip/...`) and **Kick** (`kick.com/.../clips/...`).
- 📦 **Batch Downloading (Queue Engine)**: Paste 1, 5, 20, or 50+ links at once. The engine queues, downloads, and processes them concurrently.
- 📱 **Smart 9:16 Reel Conversion**:
  - **Dynamic Blurred Background**: Places the full 16:9 stream centered over an aesthetically blurred, color-matched background. Zero gameplay or facecam is cut off!
  - **Ultra-Fast FFmpeg Pipeline**: Downsamples background before blurring to deliver **10x to 15x faster encoding** (processes in ~15-20 seconds per clip).
  - **Centered Full-Screen Crop**: Alternative clean vertical crop for action-centered moments.
- 🖥️ **16:9 PC Landscape Mode**: Exports the original resolution (1080p/720p 60fps) without re-scaling, ready for PC playback or YouTube edits.
- 🎨 **Modern Dark Web UI**: Sleek Twitch-purple & Kick-neon green interface with real-time progress bars, status indicators, and glassmorphism.
- 📥 **Flexible Downloads**: Download individual processed MP4 files or grab everything in a single consolidated **.ZIP** archive in one click.
- 🌐 **100% Free Hosting Ready (0 DHS)**: Designed to run locally with 1-click launcher, or deployable on Hugging Face Spaces / Render free tiers.

---

## 📐 Output Video Formats

| Format | Aspect Ratio | Resolution | Best For |
|---|---|---|---|
| **📱 Reel (Blurred BG)** *(Recommended)* | **9:16** | 1080 x 1920 | TikTok, Instagram Reels, YouTube Shorts (Full stream visible, stylish blurred backdrop) |
| **✂️ Reel (Centered Crop)** | **9:16** | 1080 x 1920 | TikTok / Shorts when the streamer/action is strictly in the middle |
| **🖥️ PC Video (Landscape)** | **16:9** | 1920 x 1080 / Native | PC montages, standard YouTube uploads, archive |

---

## 🚀 Quick Start (Local)

### Prerequisites
- [Python 3.10+](https://www.python.org/) installed
- [FFmpeg](https://ffmpeg.org/) installed (automatically detected on Windows via WinGet or PATH)

### 1. Clone the repository
```bash
git clone https://github.com/mojzak/Clipper-Pro.git
cd Clipper-Pro
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Application

#### Option A: Windows 1-Click Launcher (Easiest)
Double-click on:
```bash
start.bat
```
*This automatically starts the server and opens your browser at `http://localhost:8000`.*

#### Option B: Terminal Command
```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
Open **`http://localhost:8000`** in your browser.

---

## 💻 CLI Usage (Terminal Automation)

For command-line automation and scripting without a browser:

1. Add your links (one per line) in `links.txt`:
```text
https://clips.twitch.tv/WiseFaithfulClips...
https://kick.com/streamer?clip=clip_12345...
```

2. Run the CLI tool:
```bash
# Export in Reel format with blurred background (default)
python cli.py -m reel_blur

# Export in Reel format with centered crop
python cli.py -m reel_crop

# Export in PC 16:9 Landscape format
python cli.py -m landscape
```
Converted videos are automatically saved in `downloads/processed/`.

---

## 🌐 Free Cloud Deployment (0 DHS)

### Option A: Hugging Face Spaces (Gradio SDK - 100% Free)
1. Create a free account on [huggingface.co](https://huggingface.co).
2. Click **New Space** ➔ Name: `clipper-pro`.
3. Choose:
   - **SDK**: `Gradio` (Blank template)
   - **Hardware**: `CPU Basic (Free - 2 vCPU, 16 GB RAM)` *(Important: Choose CPU Basic, not ZeroGPU)*.
4. Push or upload these files: `app.py`, `packages.txt`, `requirements.txt`, `downloader.py`, `converter.py`.
5. Hugging Face builds the Space and generates an HTTPS public URL you can access from your PC or mobile phone 24/7!

### Option B: Docker / Render.com
Use the included `Dockerfile`:
```bash
docker build -t clipper-pro .
docker run -p 7860:7860 clipper-pro
```

---

## 📂 Project Structure

```text
Clipper-Pro/
├── main.py              # FastAPI server, batch queue & REST API endpoints
├── app.py               # Gradio web application for cloud deployment
├── downloader.py        # yt-dlp extraction engine (Twitch & Kick)
├── converter.py         # Optimized multi-threaded FFmpeg conversion pipeline
├── templates/
│   └── index.html       # Modern dark Web UI (Tailwind CSS & Glassmorphism)
├── cli.py               # Command-line batch interface
├── links.txt            # URLs input file template for CLI
├── requirements.txt     # Python package dependencies
├── packages.txt         # System debian dependencies (FFmpeg)
├── Dockerfile           # Production container configuration
├── start.bat            # 1-click Windows local launcher
└── README.md            # Documentation
```

---

## 🛠️ Tech Stack

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/)
- **Cloud Interface**: [Gradio](https://www.gradio.app/)
- **Media Engine**: [yt-dlp](https://github.com/yt-dlp/yt-dlp), [FFmpeg](https://ffmpeg.org/)
- **Frontend**: Tailwind CSS, HTML5, Vanilla JavaScript

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
