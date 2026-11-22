@echo off
chcp 65001 >nul
cd /d "%~dp0"

where pythonw >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw src\app.py
    exit /b 0
)

where python >nul 2>nul
if %errorlevel%==0 (
    python src\app.py
    exit /b 0
)

echo [错误] 未检测到 Python 3 环境。
echo 请先安装 Python 3（安装时勾选 Add Python to PATH）：https://www.python.org/downloads/
pause
