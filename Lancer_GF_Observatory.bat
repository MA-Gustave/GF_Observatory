@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%\src"
where py >nul 2>nul
if errorlevel 1 (
 echo Python 3.11+ requis. Installe Python puis reessaie.
 pause
 exit /b 2
)
py -3 "%CD%\GF_Observatory.pyw"
if errorlevel 1 (
 echo Echec de lancement Observatory.
 pause
 exit /b 2
)
