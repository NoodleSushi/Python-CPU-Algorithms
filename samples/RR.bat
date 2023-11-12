@echo off
cd ..
call .venv\Scripts\Activate.bat
python main.py --algo "Round Robin" --arrival "0 3 4 6 10" --burst "8 4 5 3 2" --quantum 2