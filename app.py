import os
os.environ["GRADIO_SSR_MODE"] = "false"
import zipfile
import gradio as gr
from pathlib import Path
from downloader import download_clip, detect_platform
from converter import convert_video

DOWNLOADS_DIR = Path("downloads")
PROCESSED_DIR = DOWNLOADS_DIR / "processed"
TEMP_DIR = DOWNLOADS_DIR / "temp"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

MODE_MAPPING = {
    "📱 Reel 9:16 (Fond Flou Stylé - TikTok/Reels/Shorts)": "reel_blur",
    "✂️ Reel 9:16 (Crop Centré Plein Écran)": "reel_crop",
    "🖥️ Vidéo PC 16:9 (Paysage Qualité Originale)": "landscape"
}

def process_batch(urls_text: str, format_choice: str, progress=gr.Progress()):
    if not urls_text or not urls_text.strip():
        return [], None, "❌ Veuillez coller au moins un lien Twitch ou Kick."

    lines = [l.strip() for l in urls_text.strip().splitlines() if l.strip().startswith("http")]
    if not lines:
        return [], None, "❌ Aucun lien valide détecté (commençant par http/https)."

    mode = MODE_MAPPING.get(format_choice, "reel_blur")
    output_files = []
    logs = []

    progress(0, desc="Initialisation du traitement...")

    total = len(lines)
    for idx, url in enumerate(lines, 1):
        step_base = (idx - 1) / total
        platform = detect_platform(url)
        progress(step_base + (0.1 / total), desc=f"[{idx}/{total}] Téléchargement {platform}...")

        try:
            # 1. Download
            dl_info = download_clip(url, str(TEMP_DIR))
            title = dl_info["title"]
            uploader = dl_info["uploader"]
            raw_path = dl_info["raw_filepath"]

            # 2. Convert
            progress(step_base + (0.6 / total), desc=f"[{idx}/{total}] Conversion FFmpeg ({mode})...")
            mode_suffix = "Reel_9x16" if "reel" in mode else "Paysage_16x9"
            out_filename = f"{platform}_{uploader}_{title}_{mode_suffix}.mp4"
            safe_filename = "".join(c for c in out_filename if c.isalnum() or c in " ._-").strip()
            final_output_path = PROCESSED_DIR / safe_filename

            convert_video(raw_path, str(final_output_path), mode=mode)

            # Cleanup raw temp file
            if os.path.exists(raw_path):
                try:
                    os.remove(raw_path)
                except Exception:
                    pass

            output_files.append(str(final_output_path))
            logs.append(f"✅ [{platform}] {uploader} - {title} (Prêt)")

        except Exception as e:
            logs.append(f"❌ Erreur sur {url}: {str(e)[:150]}")

    progress(1.0, desc="Traitement terminé !")

    # Generate ZIP if multiple videos
    zip_path = None
    if len(output_files) > 1:
        zip_filename = PROCESSED_DIR / f"Clips_Batch_{os.urandom(4).hex()}.zip"
        with zipfile.ZipFile(str(zip_filename), "w", zipfile.ZIP_DEFLATED) as zipf:
            for f in output_files:
                zipf.write(f, arcname=os.path.basename(f))
        zip_path = str(zip_filename)
    elif len(output_files) == 1:
        zip_path = output_files[0]

    log_summary = "\n".join(logs)
    return output_files, zip_path, log_summary


# Gradio UI Theme & Layout
custom_theme = gr.themes.Default(
    primary_hue="purple",
    secondary_hue="emerald",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Plus Jakarta Sans"), "sans-serif"]
)

with gr.Blocks(title="Clipper Pro - Twitch & Kick Downloader") as demo:
    gr.Markdown(
        """
        # 🎬 Clipper Pro • Twitch & Kick Batch Downloader
        ### Téléchargez et convertissez plusieurs clips d'un coup en **Reel 9:16 (TikTok/Shorts)** ou en **16:9 PC** !
        """
    )

    with gr.Row():
        with gr.Column(scale=2):
            urls_input = gr.Textbox(
                label="Liens Twitch & Kick (Un par ligne)",
                placeholder="https://clips.twitch.tv/WiseFaithful...\nhttps://www.twitch.tv/streamer/clip/...\nhttps://kick.com/streamer?clip=...",
                lines=6
            )
            format_radio = gr.Radio(
                label="Format de sortie vidéo",
                choices=list(MODE_MAPPING.keys()),
                value="📱 Reel 9:16 (Fond Flou Stylé - TikTok/Reels/Shorts)",
                info="Le mode Fond Flou conserve toute l'action du stream au format vertical mobile."
            )
            btn_run = gr.Button("⚡ Télécharger et Convertir le lot", variant="primary", size="lg")

        with gr.Column(scale=2):
            status_text = gr.Textbox(label="Journal de traitement", lines=6, interactive=False)
            zip_output = gr.File(label="📦 Télécharger les vidéos (Archive ZIP ou Fichier MP4)")
            video_gallery = gr.Files(label="Fichiers MP4 individuels")

    btn_run.click(
        fn=process_batch,
        inputs=[urls_input, format_radio],
        outputs=[video_gallery, zip_output, status_text]
    )

demo.launch(ssr_mode=False)
