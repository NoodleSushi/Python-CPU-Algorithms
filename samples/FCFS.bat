@echo off
cd ..
call .venv\Scripts\activate
python main.py --algo "First Come First Serve" --arrival "0 3 4 6 10" --burst "8 4 5 3 2"