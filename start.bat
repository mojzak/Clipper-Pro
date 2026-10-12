@echo off
title Clipper Pro - Twitch and Kick Downloader
echo ===================================================
echo   Clipper Pro - Twitch and Kick Batch Downloader
echo ===================================================
echo.

echo Verification de Python...
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Python n'est pas detecte. Veuillez installer Python 3.
    pause
    exit /b
)

echo Lancement du serveur Web local...
echo.
echo ===================================================
echo   Application disponible sur : http://localhost:8000
echo ===================================================
echo Appuyez sur Ctrl+C pour arreter le serveur.
echo.

start http://localhost:8000
py -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
pause
