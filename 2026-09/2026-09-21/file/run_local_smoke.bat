@echo off
cd /d G:\project\work_record\2026-09\2026-09-21\file
python -u run_local_smoke.py > local_run.stdout.log 2> local_run.stderr.log
echo EXIT_CODE=%ERRORLEVEL% >> local_run.stdout.log
