@echo off
setlocal
set DEST=D:\models\qwen-image-2.1\diffusion_models
set URL=https://hf-mirror.com/abenzerps/Qwen-Image-2.1-GGUF/resolve/main/qwen-image-2.1-Q4_K_M.gguf
mkdir "%DEST%" 2>nul
curl -L --retry 5 --retry-delay 10 -C - -o "%DEST%\qwen-image-2.1-Q4_K_M.gguf" "%URL%" > "G:\project\work_record\2026-09\2026-09-21\file\download_q4k.log" 2>&1
echo EXIT_CODE=%ERRORLEVEL% >> "G:\project\work_record\2026-09\2026-09-21\file\download_q4k.log"
