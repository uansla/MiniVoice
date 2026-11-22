@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo 正在检查 PyInstaller...
python -m pip show pyinstaller >nul 2>nul
if %errorlevel% neq 0 (
    echo 正在安装 PyInstaller...
    python -m pip install pyinstaller
)

echo 正在打包独立可执行文件...
python -m PyInstaller --noconfirm --onefile --windowed --name "MiniVoice" src\app.py

echo.
echo 打包完成！生成的 exe 位于 dist\MiniVoice.exe
echo 注意：请将 dist\MiniVoice.exe 放到项目根目录（与 config 文件夹同级）运行。
pause
