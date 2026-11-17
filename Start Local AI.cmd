@echo off
cd /d "%~dp0"
set "AGILITECH_MODEL_FILE=..\..\work\ollama-models\blobs\sha256-7f4030143c1c477224c5434f8272c662a8b042079a0a584f0a27a1684fe2e1fa"
if exist "..\..\work\ollama-runtime\lib\ollama\llama-server.exe" if exist "%AGILITECH_MODEL_FILE%" goto workspace_model
where ollama >nul 2>nul
if errorlevel 1 (
  echo Install Ollama from https://ollama.com/download and follow the AI setup in README.md.
  echo Navigation help and source excerpts work in Library Guide mode without a model.
  pause
  exit /b 1
)
set "OLLAMA_HOST=127.0.0.1:11434"
set "OLLAMA_NO_CLOUD=1"
set "OLLAMA_NOHISTORY=1"
echo Starting local Ollama. First download qwen3:0.6b as described in README.md.
ollama serve
goto finished
:workspace_model
echo Starting the downloaded local CPU model. Keep this window open; Ctrl+C stops the model.
"..\..\work\ollama-runtime\lib\ollama\llama-server.exe" -m "%AGILITECH_MODEL_FILE%" --host 127.0.0.1 --port 11434 --alias qwen3:0.6b --ctx-size 4096 --threads 4 --parallel 1 --jinja --reasoning off --no-webui
:finished
echo If the port is already in use, a local model server may already be running.
pause
