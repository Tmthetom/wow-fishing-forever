@echo off
setlocal
set "RIVER_PY="
set "WOWFISH_HOME=%~dp0.local\state"
if not exist "%~dp0.venv\pyvenv.cfg" goto missing
for /f "usebackq tokens=1,* delims== " %%A in ("%~dp0.venv\pyvenv.cfg") do if "%%A"=="home" set "RIVER_PY=%%B"
if not defined RIVER_PY goto missing
if not exist "%RIVER_PY%\pythonw.exe" goto missing
if /i "%~1"=="doctor" (
    "%~dp0.venv\Scripts\python.exe" -I -m wowfish doctor
    exit /b
)
start "" /d "%~dp0." "%RIVER_PY%\pythonw.exe" -I "%~dp0scripts\river_desk.py" --randomize
exit /b

:missing
echo Local Python is missing or could not be started. Run uv sync first.
pause
exit /b 1
