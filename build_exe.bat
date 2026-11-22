@echo off
chcp 65001 >nul
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (set "PY=py -3") else (set "PY=python")

echo 正在安装 PyInstaller...
%PY% -m pip install --upgrade pyinstaller
if errorlevel 1 goto :failed

echo 正在构建 Windows 可移植目录...
%PY% -m PyInstaller --noconfirm --clean --windowed --onedir --name MiniVoice --paths src src\app.py
if errorlevel 1 goto :failed

echo 正在复制配置和说明...
if exist dist\MiniVoice\config rmdir /s /q dist\MiniVoice\config
xcopy config dist\MiniVoice\config /E /I /Y >nul
xcopy scripts dist\MiniVoice\scripts /E /I /Y >nul
xcopy vst_plugins dist\MiniVoice\vst_plugins /E /I /Y >nul
copy README.md dist\MiniVoice\README.md >nul
if errorlevel 1 goto :failed

powershell -NoProfile -Command "Compress-Archive -Path 'dist\MiniVoice\*' -DestinationPath 'dist\MiniVoice-windows-x64.zip' -Force"
if errorlevel 1 goto :failed

echo.
echo 构建完成：dist\MiniVoice\MiniVoice.exe
echo 测试包：dist\MiniVoice-windows-x64.zip
echo 请解压整个目录后运行 MiniVoice.exe。
pause
exit /b 0

:failed
echo.
echo [错误] 构建或打包失败，请查看上方错误信息。
pause
exit /b 1
