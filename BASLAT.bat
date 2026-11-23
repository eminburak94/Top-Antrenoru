@echo off
title Top Antrenoru v0.8.9 Playtest Beta
cd /d "%~dp0"
where py >nul 2>&1
if errorlevel 1 (
  python -B oyun.py
) else (
  py -3 -B oyun.py
)
if errorlevel 1 pause

