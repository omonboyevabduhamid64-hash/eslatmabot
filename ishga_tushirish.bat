@echo off
chcp 65001 > nul
title EslatmaBot - Esingizdami Hojayin
echo ===================================================
echo         EslatmaBot ishga tushirilmoqda...
echo ===================================================
cd /d "%~dp0"
python main.py
if errorlevel 1 (
    echo.
    echo Xatolik yuz berdi! Iltimos, yuqoridagi xabarni ko'ring.
)
pause
