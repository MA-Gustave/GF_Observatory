@echo off
setlocal
cd /d "%~dp0"
where pyw.exe >nul 2>&1
if %ERRORLEVEL% EQU 0 (
  start "" pyw.exe -3 "%~dp0GF_Observatory_Diagnostic.pyw"
  exit /b 0
)
where pythonw.exe >nul 2>&1
if %ERRORLEVEL% EQU 0 (
  start "" pythonw.exe "%~dp0GF_Observatory_Diagnostic.pyw"
  exit /b 0
)
echo Python 3 (avec Tkinter) est requis.
pause
exit /b 1
