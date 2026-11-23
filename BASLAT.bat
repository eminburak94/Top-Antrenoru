@echo off
setlocal
title Top Antrenoru v0.9.1 Playtest Beta
cd /d "%~dp0" || goto :failed
for %%F in (data.json tarihsel_girisler.json tarihsel_skorlar.json) do (
  if not exist "%%F" (
    echo Eksik oyun verisi / Missing game data: %%F
    goto :failed
  )
)
py -3 -c "import tkinter" >nul 2>&1
if not errorlevel 1 (
  py -3 -B -X utf8 oyun.py %*
  if errorlevel 1 goto :failed
  exit /b 0
)
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
  echo Python ve Tcl/Tk gerekli / Python with Tcl/Tk is required.
  goto :failed
)
python -B -X utf8 oyun.py %*
if not errorlevel 1 exit /b 0

:failed
if "%~1"=="" pause
exit /b 1

