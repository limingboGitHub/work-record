@echo off
cd /d G:\project\work_record\2026-09\2026-09-21\file
python -u run_after_kitchen.py > after_kitchen.out.log 2> after_kitchen.err.log
echo EXIT_CODE=%ERRORLEVEL% >> after_kitchen.out.log
