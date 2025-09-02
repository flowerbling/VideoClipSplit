#!/bin/bash
uv run pyinstaller --noconfirm --onedir --windowed --name "视频分镜工具" --icon "assrt/icon.icns" --add-data "assrt:assrt" main.py