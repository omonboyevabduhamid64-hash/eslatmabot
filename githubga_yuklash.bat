@echo off
chcp 65001 > nul
title GitHub-ga yuklash
cd /d "C:\Users\HP\Desktop\EslatmaBot"
echo ==============================================
echo     Kodlar GitHub-ga yuklanmoqda...
echo ==============================================
git push -u origin main
echo.
if %errorlevel% equ 0 (
    echo ==============================================
    echo     MUVAFFAQIYATLI YUKLANDI!
    echo ==============================================
) else (
    echo Qandaydir xatolik yuz berdi. Iltimos yuqoridagi yozuvni tekshiring.
)
pause
