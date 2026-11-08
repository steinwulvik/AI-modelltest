@echo off
rem Kjører sammenligningen med alle aktive modeller i modeller.json. Skriver alt til kjor-logg.txt.
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
echo Kjorer testen. Lokale modeller kan bruke noen minutter. Vinduet lukkes nar det er ferdig.
.venv\Scripts\python.exe sammenlign.py %* > kjor-logg.txt 2>&1
echo === FERDIG === >> kjor-logg.txt
