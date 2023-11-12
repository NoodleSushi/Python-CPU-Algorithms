@echo off
cd ..
call .venv\Scripts\activate
python main.py --algo "Priority Non-Preemptive" --arrival "0 3 4 6 10" --burst "8 4 5 3 2" --priority "2 5 1 9 3"