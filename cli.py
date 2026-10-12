import sys
import argparse
from pathlib import Path
from downloader import download_clip, detect_platform
from converter import convert_video

def main():
    parser = argparse.ArgumentParser(description="Clipper Pro CLI - Téléchargement groupé Twitch & Kick")
    parser.add_argument("--file", "-f", default="links.txt", help="Fichier contenant la liste des URLs (1 par ligne)")
    parser.add_argument("--mode", "-m", choices=["reel_blur", "reel_crop", "landscape"], default="reel_blur",
                        help="Format de sortie (reel_blur = 9:16 flou, reel_crop = 9:16 recadré, landscape = 16:9 PC)")
    args = parser.parse_args()

    input_file = Path(args.file)
    if not input_file.exists():
        print(f"Fichier '{args.file}' introuvable. Créez-le avec vos liens ou utilisez l'interface Web (start.bat).")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip().startswith("http")]

    if not urls:
        print(f"Aucun lien valide trouvé dans '{args.file}'.")
        return

    print(f"\n🚀 Démarrage du traitement de {len(urls)} lien(s) en mode [{args.mode}]...\n")
    
    downloads_dir = Path("downloads")
    processed_dir = downloads_dir / "processed"
    temp_dir = downloads_dir / "temp"
    processed_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)

    for idx, url in enumerate(urls, 1):
        print(f"[{idx}/{len(urls)}] Téléchargement de : {url}")
        try:
            info = download_clip(url, str(temp_dir))
            print(f"  -> Titre : {info['title']} ({info['platform']})")
            print(f"  -> Conversion en cours ({args.mode})...")
            
            mode_suffix = "Reel_9x16" if "reel" in args.mode else "Paysage_16x9"
            out_name = f"{info['platform']}_{info['uploader']}_{info['title']}_{mode_suffix}.mp4"
            safe_name = "".join(c for c in out_name if c.isalnum() or c in " ._-").strip()
            final_path = processed_dir / safe_name

            convert_video(info["raw_filepath"], str(final_path), mode=args.mode)
            print(f"  ✅ Terminé : {final_path}\n")
        except Exception as e:
            print(f"  ❌ Erreur sur ce lien : {e}\n")

    print("🎉 Traitement du lot terminé ! Vos fichiers sont dans 'downloads/processed'.")

if __name__ == "__main__":
    main()
