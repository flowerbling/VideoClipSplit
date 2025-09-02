@echo off
uv run pyinstaller --noconfirm --onedir --windowed --name "视频分镜工具" --icon "assrt/icon.ico" --add-data "assrt;assrt" main.py
pause