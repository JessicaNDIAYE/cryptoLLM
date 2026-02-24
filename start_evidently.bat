@echo off
cd /d "%~dp0reporting"
pip install -r requirements.txt
python project.py
evidently ui --host 0.0.0.0 --port 8082
pause