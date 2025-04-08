@echo off
cd /d %~dp0
python\python.exe -m ensurepip
python\python.exe -m pip install --upgrade pip
python\python.exe -m pip install -r requirements.txt
python\python.exe main.py
pause