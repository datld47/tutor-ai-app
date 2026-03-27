@echo off
cd /d "%~dp0"

echo [INFO] Installing Flask if missing...
..\.venv\Scripts\python -m pip install flask

echo [INFO] Starting Chatbot...
..\.venv\Scripts\python app.py
pause
