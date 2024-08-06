#!/bin/bash

# 스크립트의 현재 디렉토리 위치 설정
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$SCRIPT_DIR"

# 가상 환경 생성
if [ ! -d ".venv" ]; then
    echo "가상 환경을 생성합니다..."
    python3 -m venv .venv
fi

# 가상 환경 활성화
source .venv/bin/activate

# 필요한 라이브러리 설치
echo "필요한 라이브러리를 설치합니다..."
pip install --upgrade pip
pip install -r requirements.txt

# 가상 환경 비활성화
deactivate

echo "설치가 완료되었습니다. 프로그램을 실행하려면 ./run.sh를 사용하세요."
