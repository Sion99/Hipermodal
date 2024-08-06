#!/bin/bash

# 스크립트의 현재 디렉토리 위치 설정
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$SCRIPT_DIR"

# 가상 환경 활성화
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "가상 환경을 활성화했습니다."

    # 프로그램 실행
    echo "프로그램을 실행합니다..."
    python main.py

    # 가상 환경 비활성화
    deactivate
else
    echo "가상 환경이 존재하지 않습니다. 먼저 ./install.sh를 실행하여 설치를 완료하세요."
fi
