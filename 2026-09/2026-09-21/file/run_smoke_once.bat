@echo off
cd /d G:\project\work_record\2026-09\2026-09-21\file
python -u submit_smoke_once.py > smoke_once.out.log 2> smoke_once.err.log
echo EXIT_CODE=%ERRORLEVEL% >> smoke_once.out.log
