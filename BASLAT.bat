@echo off
title Top Antrenoru v0.8.7
cd /d "%~dp0"
where py >nul 2>&1
if errorlevel 1 (
  python -B oyun.py
) else (
  py -3 -B oyun.py
)
if errorlevel 1 pause

