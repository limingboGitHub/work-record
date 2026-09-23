@echo off
cd /d G:\project\work_record\2026-09\2026-09-21\file
python -u download_qwen_image21_weights.py > download_weights.log 2> download_weights.err.log
echo EXIT_CODE=%ERRORLEVEL% >> download_weights.log
