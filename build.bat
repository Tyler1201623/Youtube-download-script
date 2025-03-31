:: filepath: /c:/Users/ty/Desktop/Best Programs I Created/Youtube Download Script/build.bat
@echo off

:: Change to script directory
cd /d "%~dp0"

:: Check for administrator privileges (but warn it's not recommended)
echo Note: Administrator privileges are not required...
echo Building in: %CD%
echo.

echo Cleaning previous build...
:: Force delete dist folder
taskkill /F /IM "YouTube Downloader Pro.exe" >nul 2>&1
rd /s /q "dist" 2>nul
rd /s /q "build" 2>nul
del /f /q "*.spec" 2>nul

echo Building YouTube Downloader Pro...
python -m PyInstaller ^
    --clean ^
    --noconfirm ^
    --name "YouTube Downloader Pro" ^
    --windowed ^
    --icon=icon.ico ^
    --hidden-import tkinter ^
    --hidden-import ttkthemes ^
    --hidden-import PIL ^
    --hidden-import yt_dlp ^
    --hidden-import urllib3 ^
    --hidden-import brotli ^
    --hidden-import certifi ^
    --hidden-import ffmpeg ^
    --add-data "EULA.md;." ^
    --add-data "LICENSE.md;." ^
    --add-data "DISCLAIMER.md;." ^
    --onefile ^
    main.py

if %errorlevel% equ 0 (
    echo.
    echo Build successful! 
    echo.
    echo Note: User data will be stored in: %%APPDATA%%\YouTube Downloader Pro
    echo - Downloads: %%APPDATA%%\YouTube Downloader Pro\downloads
    echo - Log file:  %%APPDATA%%\YouTube Downloader Pro\activity.log
    echo.
    explorer "dist"
) else (
    echo.
    echo Build failed! Check the error messages above.
    echo.
)
pause