@echo off
cd ..
call .venv\Scripts\Activate.bat
python main.py --algo "Shortest Job First" --arrival "0 3 4 6 10" --burst "8 4 5 3 2"