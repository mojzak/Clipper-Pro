# Dockerfile pour déploiement 100% gratuit (Hugging Face Spaces / Render / Koyeb)
FROM python:3.11-slim

# Installation de FFmpeg et curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copie des dépendances et installation
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie de l'application
COPY . .

# Création des dossiers de téléchargement
RUN mkdir -p downloads/processed downloads/temp

# Port standard (Hugging Face Spaces utilise 7860, Render utilise PORT)
ENV PORT=7860
EXPOSE 7860

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-7860}"]
