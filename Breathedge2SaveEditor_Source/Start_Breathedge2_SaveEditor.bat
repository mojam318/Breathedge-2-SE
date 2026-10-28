@echo off
setlocal
if exist "%~dp0Breathedge2SaveEditor.exe" (
  start "" "%~dp0Breathedge2SaveEditor.exe"
  exit /b
)
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 "%~dp0Breathedge2SaveEditor.py"
) else (
  python "%~dp0Breathedge2SaveEditor.py"
)
