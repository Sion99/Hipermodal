#!/bin/bash

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$SCRIPT_DIR"

# Activate
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "Virtual environment activated"

    # 프로그램 실행
    echo "Starting..."
    python main.py

    # 가상 환경 비활성화
    deactivate
else
    echo "No virtual environment available. Please run install.sh to complete installation."
fi
