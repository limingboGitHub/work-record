@echo off
cd /d D:\ComfyUI_windows_portable
python_embeded\python.exe -s ComfyUI\main.py --windows-standalone-build --lowvram --disable-smart-memory --listen 127.0.0.1 --port 8188
