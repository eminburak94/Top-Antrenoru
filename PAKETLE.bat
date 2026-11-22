@echo off
setlocal
cd /d "%~dp0"
if not "%TOP_ANTRENORU_BUILD_TOOLS%"=="" set "PYTHONPATH=%TOP_ANTRENORU_BUILD_TOOLS%;%PYTHONPATH%"
python -B -m PyInstaller --noconfirm --onedir --windowed --name "Top Antrenoru" --distpath "v0.8.7 TESTER BETA" --workpath ".build\work" --specpath ".build" --add-data "%~dp0data.json;." --add-data "%~dp0tarihsel_girisler.json;." --add-data "%~dp0tarihsel_skorlar.json;." oyun.py
exit /b %errorlevel%
