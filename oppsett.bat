@echo off
rem Oppsett for AI-modelltest: steg 1-3 i README. Skriver alt til oppsett-logg.txt.
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
rem Python 3.15 har ingen ferdigbygd PyYAML ennå. Dette bygger den uten C-del, så det trengs ingen kompilator.
set PYYAML_FORCE_LIBYAML=0
set LOGG=oppsett-logg.txt

echo === Steg 1: Python-versjon === > %LOGG%
python --version >> %LOGG% 2>&1
if errorlevel 1 (
  echo RESULTAT: Python mangler eller er ikke i PATH >> %LOGG%
  goto slutt
)
python -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >> %LOGG% 2>&1
if errorlevel 1 (
  echo RESULTAT: Python er eldre enn 3.10 >> %LOGG%
  goto slutt
)
echo RESULTAT: Python OK >> %LOGG%

echo === Steg 2: virtuelt miljo og DSPy === >> %LOGG%
if not exist .venv\Scripts\python.exe python -m venv .venv >> %LOGG% 2>&1
.venv\Scripts\python.exe -m pip install --upgrade pip >> %LOGG% 2>&1
.venv\Scripts\python.exe -m pip install -r requirements.txt >> %LOGG% 2>&1
if errorlevel 1 (
  echo RESULTAT: Installasjon feilet >> %LOGG%
  goto slutt
)
echo RESULTAT: DSPy installert >> %LOGG%

echo === Steg 3: provekjoring med falsk modell === >> %LOGG%
.venv\Scripts\python.exe sammenlign.py --test >> %LOGG% 2>&1
if errorlevel 1 (
  echo RESULTAT: Provekjoringen feilet >> %LOGG%
  goto slutt
)
echo RESULTAT: Provekjoring OK >> %LOGG%

:slutt
echo === FERDIG === >> %LOGG%
