import os
import shutil
import subprocess
import glob
from pathlib import Path

def find_ffmpeg() -> str:
    """Detect ffmpeg path from PATH, WinGet packages, or local directories."""
    # 1. Standard PATH
    which_path = shutil.which("ffmpeg")
    if which_path:
        return which_path

    # 2. Local bin or tools dir
    local_candidates = [
        Path(__file__).parent / "ffmpeg.exe",
        Path(__file__).parent / "tools" / "ffmpeg.exe",
        Path(__file__).parent / "tools" / "bin" / "ffmpeg.exe",
    ]
    for cand in local_candidates:
        if cand.exists():
            return str(cand)

    # 3. Check AppData WinGet directories
    user_appdata = os.environ.get("LOCALAPPDATA", "")
    if user_appdata:
        winget_pattern = os.path.join(user_appdata, "Microsoft", "WinGet", "Packages", "*ffmpeg*", "**", "ffmpeg.exe")
        matches = glob.glob(winget_pattern, recursive=True)
        if matches:
            return matches[0]

    # 4. Check Program Files
    prog_files = [os.environ.get("ProgramFiles", "C:\\Program Files"), os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")]
    for pf in prog_files:
        matches = glob.glob(os.path.join(pf, "*ffmpeg*", "**", "ffmpeg.exe"), recursive=True)
        if matches:
            return matches[0]

    return "ffmpeg"  # Fallback to system command


def convert_video(input_path: str, output_path: str, mode: str = "landscape") -> bool:
    """
    Converts video based on selected mode:
    - landscape: PC standard 16:9 MP4 (normalized if needed).
    - reel_blur: 9:16 vertical (1080x1920) with blurred background + sharp centered foreground (Recommended for TikTok/Reels/Shorts).
    - reel_crop: 9:16 vertical (1080x1920) centered crop.
    """
    ffmpeg_bin = find_ffmpeg()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if mode == "reel_blur":
        # Ultra-fast high-quality blurred background:
        # Scale background to low-res (270x480), apply fast blur, then upscale to 1080x1920 (15x faster!)
        filter_complex = (
            "[0:v]scale=270:480:force_original_aspect_ratio=increase,"
            "crop=270:480,boxblur=6:2,scale=1080:1920:flags=bilinear,"
            "eq=brightness=-0.08:contrast=1.05[bg];"
            "[0:v]scale=1080:-2[fg];"
            "[bg][fg]overlay=(W-w)/2:(H-h)/2[v]"
        )
        cmd = [
            ffmpeg_bin, "-y",
            "-threads", "0",
            "-i", input_path,
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-map", "0:a?",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "192k",
            output_path
        ]
    elif mode == "reel_crop":
        filter_str = "crop=ih*9/16:ih:(iw-ow)/2:0,scale=1080:1920"
        cmd = [
            ffmpeg_bin, "-y",
            "-threads", "0",
            "-i", input_path,
            "-vf", filter_str,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "192k",
            output_path
        ]
    else:
        # Standard landscape (16:9 PC)
        cmd = [
            ffmpeg_bin, "-y",
            "-threads", "0",
            "-i", input_path,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "20",
            "-c:a", "aac",
            "-b:a", "192k",
            output_path
        ]

    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr}")
        raise RuntimeError(f"FFmpeg failed: {e.stderr[-300:] if e.stderr else 'Unknown error'}")
