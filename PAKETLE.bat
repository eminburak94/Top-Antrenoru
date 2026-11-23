@echo off
setlocal
cd /d "%~dp0"
if not "%TOP_ANTRENORU_BUILD_TOOLS%"=="" set "PYTHONPATH=%TOP_ANTRENORU_BUILD_TOOLS%;%PYTHONPATH%"
if not defined TOP_ANTRENORU_DIST set "TOP_ANTRENORU_DIST=v0.9.2 PLAYTEST BETA"
if not defined TOP_ANTRENORU_WORK set "TOP_ANTRENORU_WORK=.build\v092-work"
python -B -m PyInstaller --noconfirm --onedir --windowed --name "Top Antrenoru" --distpath "%TOP_ANTRENORU_DIST%" --workpath "%TOP_ANTRENORU_WORK%" --specpath ".build" --add-data "%~dp0data.json;." --add-data "%~dp0tarihsel_girisler.json;." --add-data "%~dp0tarihsel_skorlar.json;." oyun.py
exit /b %errorlevel%
