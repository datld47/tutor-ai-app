@echo off
echo Starting fix script... > run_log.txt
.venv\Scripts\python.exe fix_json_content.py >> run_log.txt 2>&1
echo Done. >> run_log.txt
type run_log.txt
