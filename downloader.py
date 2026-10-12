import os
import re
import yt_dlp
from typing import Callable, Optional, Dict, Any

def sanitize_filename(name: str) -> str:
    """Sanitize string to be safe as a Windows / Linux filename."""
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = name.strip()
    return name[:80] if len(name) > 80 else name

def detect_platform(url: str) -> str:
    url_lower = url.lower()
    if "twitch.tv" in url_lower:
        return "Twitch"
    if "kick.com" in url_lower:
        return "Kick"
    return "Video"

def get_clip_info(url: str) -> Dict[str, Any]:
    """Extract metadata without downloading."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "title": info.get("title", "Sans titre"),
            "uploader": info.get("uploader") or info.get("channel", "Inconnu"),
            "duration": info.get("duration", 0),
            "thumbnail": info.get("thumbnail", ""),
            "platform": detect_platform(url)
        }

def download_clip(
    url: str,
    output_dir: str,
    progress_callback: Optional[Callable[[float, str], None]] = None
) -> Dict[str, Any]:
    """
    Downloads the best video/audio for Twitch or Kick clip using yt-dlp.
    Returns metadata and downloaded file path.
    """
    os.makedirs(output_dir, exist_ok=True)
    platform = detect_platform(url)

    def hook(d):
        if d.get("status") == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0)
            if total > 0 and progress_callback:
                pct = round((downloaded / total) * 100, 1)
                speed = d.get("_speed_str", "")
                progress_callback(pct, f"Téléchargement {pct}% ({speed})")
        elif d.get("status") == "finished":
            if progress_callback:
                progress_callback(100.0, "Téléchargement terminé, préparation conversion...")

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": os.path.join(output_dir, f"{platform}_%(id)s_raw.%(ext)s"),
        "progress_hooks": [hook],
        "quiet": True,
        "no_warnings": True,
        "merge_output_format": "mp4",
        # Extra headers / options for stability
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        raw_filepath = ydl.prepare_filename(info)
        
        # If output was merged or extension changed to .mp4
        if not os.path.exists(raw_filepath):
            base, _ = os.path.splitext(raw_filepath)
            if os.path.exists(base + ".mp4"):
                raw_filepath = base + ".mp4"
            elif os.path.exists(base + ".mkv"):
                raw_filepath = base + ".mkv"

        title = sanitize_filename(info.get("title", f"Clip_{info.get('id', 'video')}"))
        uploader = sanitize_filename(info.get("uploader") or info.get("channel", "Streamer"))

        return {
            "id": info.get("id"),
            "title": title,
            "uploader": uploader,
            "platform": platform,
            "raw_filepath": raw_filepath,
            "duration": info.get("duration", 0),
            "thumbnail": info.get("thumbnail", "")
        }
