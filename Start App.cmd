@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  set "AGILITECH_PYTHON=.venv\Scripts\python.exe"
) else if exist "..\..\work\.venv\Scripts\python.exe" (
  set "AGILITECH_PYTHON=..\..\work\.venv\Scripts\python.exe"
) else (
  echo Please follow the first-time setup in README.md to create .venv and install requirements.
  pause
  exit /b 1
)
echo Open http://localhost:8501 in your browser. Press Ctrl+C here to stop the app.
"%AGILITECH_PYTHON%" -m streamlit run app.py
pause
