@echo off
cd /d C:\TRASA
call .venv\Scripts\activate.bat
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
pause


