@echo off
setlocal

REM Check if project exists
IF EXIST "hipermodal" (
    echo Hipermodal already exists. Delete it or install in diffrent directory.
    exit /b 1
)

echo Cloning git repository...

REM Clone git repository
git clone https://github.com/Sion99/Hipermodal.git hipermodal
cd hipermodal

REM Create virtual environment
IF NOT EXIST ".venv" (
    echo 가상 환경을 생성하는 중...
    python -m venv .venv
)

REM Activate
CALL .venv\Scripts\activate.bat

REM Install required libraries
echo Installing required dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Deactivate
CALL deactivate

echo Installation complete. To run this program, excute run.bat
