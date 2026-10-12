import os
import uuid
import zipfile
import asyncio
from pathlib import Path
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from downloader import download_clip, detect_platform
from converter import convert_video, find_ffmpeg

BASE_DIR = Path(__file__).resolve().parent
DOWNLOADS_DIR = BASE_DIR / "downloads"
PROCESSED_DIR = DOWNLOADS_DIR / "processed"
TEMP_DIR = DOWNLOADS_DIR / "temp"

DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Twitch & Kick Clipper Pro")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# In-memory batch store (can be replaced by SQLite/Redis in production)
batches: Dict[str, Dict[str, Any]] = {}
executor = ThreadPoolExecutor(max_workers=3)

class BatchRequest(BaseModel):
    urls: List[str]
    mode: str = "reel_blur"  # "reel_blur", "reel_crop", "landscape"


def process_single_item(batch_id: str, item_index: int, url: str, mode: str):
    item = batches[batch_id]["items"][item_index]
    item["status"] = "downloading"
    item["platform"] = detect_platform(url)

    def on_progress(pct: float, msg: str):
        item["progress"] = pct
        item["message"] = msg

    try:
        # 1. Download source
        item["message"] = "Téléchargement en cours..."
        dl_info = download_clip(url, str(TEMP_DIR), progress_callback=on_progress)
        
        item["title"] = dl_info["title"]
        item["uploader"] = dl_info["uploader"]
        item["thumbnail"] = dl_info["thumbnail"]
        raw_path = dl_info["raw_filepath"]

        # 2. Conversion
        item["status"] = "converting"
        item["progress"] = 70.0
        mode_suffix = "Reel_9x16" if "reel" in mode else "Paysage_16x9"
        out_filename = f"{item['platform']}_{dl_info['uploader']}_{dl_info['title']}_{mode_suffix}.mp4"
        # Sanitize filename
        safe_filename = "".join(c for c in out_filename if c.isalnum() or c in " ._-").strip()
        final_output_path = PROCESSED_DIR / safe_filename

        item["message"] = "Conversion vidéo FFmpeg en cours..."
        convert_video(raw_path, str(final_output_path), mode=mode)

        # Cleanup raw temp file
        try:
            if os.path.exists(raw_path):
                os.remove(raw_path)
        except Exception:
            pass

        item["status"] = "done"
        item["progress"] = 100.0
        item["filename"] = safe_filename
        item["download_url"] = f"/api/download/{safe_filename}"
        item["message"] = "Prêt à être téléchargé !"

    except Exception as e:
        item["status"] = "error"
        item["message"] = str(e)
        item["progress"] = 0.0


def run_batch_tasks(batch_id: str, mode: str):
    items = batches[batch_id]["items"]
    for idx, item in enumerate(items):
        try:
            process_single_item(batch_id, idx, item["url"], mode)
        except Exception as e:
            item["status"] = "error"
            item["message"] = str(e)
    batches[batch_id]["is_completed"] = True


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    ffmpeg_detected = find_ffmpeg() != "ffmpeg" or os.system("ffmpeg -version >nul 2>&1") == 0
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"ffmpeg_ready": ffmpeg_detected}
    )


@app.post("/api/batch")
async def create_batch(req: BatchRequest, background_tasks: BackgroundTasks):
    cleaned_urls = [u.strip() for u in req.urls if u.strip().startswith("http")]
    if not cleaned_urls:
        raise HTTPException(status_code=400, detail="Aucun lien valide fourni.")

    batch_id = str(uuid.uuid4())
    batches[batch_id] = {
        "id": batch_id,
        "mode": req.mode,
        "is_completed": False,
        "items": [
            {
                "url": url,
                "platform": detect_platform(url),
                "title": "En attente...",
                "uploader": "Inconnu",
                "thumbnail": "",
                "status": "pending",
                "progress": 0.0,
                "message": "En file d'attente...",
                "filename": None,
                "download_url": None,
            }
            for url in cleaned_urls
        ]
    }

    background_tasks.add_task(run_batch_tasks, batch_id, req.mode)
    return {"batch_id": batch_id, "count": len(cleaned_urls)}


@app.get("/api/batch/{batch_id}")
async def get_batch_status(batch_id: str):
    if batch_id not in batches:
        raise HTTPException(status_code=404, detail="Batch introuvable.")
    return batches[batch_id]


@app.get("/api/download/{filename}")
async def download_file(filename: str):
    safe_path = PROCESSED_DIR / filename
    if not safe_path.exists():
        raise HTTPException(status_code=404, detail="Fichier non trouvé.")
    return FileResponse(
        path=str(safe_path),
        filename=filename,
        media_type="video/mp4"
    )


@app.get("/api/batch/{batch_id}/zip")
async def download_batch_zip(batch_id: str):
    if batch_id not in batches:
        raise HTTPException(status_code=404, detail="Batch non trouvé.")
    
    batch = batches[batch_id]
    completed_items = [it for it in batch["items"] if it.get("status") == "done" and it.get("filename")]
    
    if not completed_items:
        raise HTTPException(status_code=400, detail="Aucune vidéo prête à être compressée.")

    zip_filename = f"Clips_Batch_{batch_id[:8]}.zip"
    zip_path = DOWNLOADS_DIR / zip_filename

    with zipfile.ZipFile(str(zip_path), "w", zipfile.ZIP_DEFLATED) as zipf:
        for item in completed_items:
            f_path = PROCESSED_DIR / item["filename"]
            if f_path.exists():
                zipf.write(str(f_path), arcname=item["filename"])

    return FileResponse(
        path=str(zip_path),
        filename=zip_filename,
        media_type="application/zip"
    )


@app.get("/api/health")
async def health_check():
    ffmpeg_path = find_ffmpeg()
    return {
        "status": "ok",
        "ffmpeg": ffmpeg_path,
        "processed_videos_count": len(list(PROCESSED_DIR.glob("*.mp4")))
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
