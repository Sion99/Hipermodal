@echo off
setlocal

SET SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Activate
IF EXIST ".venv" (
    CALL .venv\Scripts\activate.bat
    echo Virtual environment activated

    REM 프로그램 실행
    echo Starting...
    python main.py

    REM 가상 환경을 비활성화합니다.
    CALL deactivate
) ELSE (
    echo No virtual environment available. Please run install.sh to complete installation.
)

endlocal
