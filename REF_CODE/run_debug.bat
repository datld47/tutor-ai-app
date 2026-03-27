@echo off
call .venv\Scripts\activate.bat
python test_write.py
python --version
echo BAT run complete
