@echo off
rem Sjekker hvilke modeller API-nøklene dine har tilgang til. Skriver til modeller-tilgjengelige.txt.
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
.venv\Scripts\python.exe sjekk_modeller.py > sjekk-logg.txt 2>&1
