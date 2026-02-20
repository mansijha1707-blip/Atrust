@echo off
echo Starting Atrust Backend...
set PYTHONPATH=%~dp0lib
cd /d %~dp0
py -m uvicorn main:app --reload
pause
