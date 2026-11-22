#Requires -RunAsAdministrator
<#
.SYNOPSIS
    极简变声 (MiniVoice) 依赖组件一键安装脚本：
    1. Equalizer APO (required system audio processing engine)
    2. SteelSeries GG/Sonar (optional noise reduction)
#>

$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  极简变声 (MiniVoice) - 依赖组件一键安装脚本" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

$OfflineInstaller = Join-Path $PSScriptRoot "..\dependencies\EqualizerAPO-x64-1.4.2.exe"
if (Test-Path $OfflineInstaller) {
    Write-Host "正在启动随测试包提供的 Equalizer APO 1.4.2 安装程序..." -ForegroundColor Green
    $process = Start-Process -FilePath $OfflineInstaller -Wait -PassThru
    if ($process.ExitCode -ne 0) {
        throw "Equalizer APO 安装程序退出代码：$($process.ExitCode)"
    }
} else {
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        throw "未找到随包安装程序，也未检测到 winget。请下载完整 GitHub Windows 测试包，或先安装 winget。"
    }
    Write-Host "正在通过 winget 安装 Equalizer APO..." -ForegroundColor Green
    winget install --id JonasThedering.EqualizerAPO -e --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) { throw "winget 安装 Equalizer APO 失败，退出代码：$LASTEXITCODE" }
}

$installSonar = Read-Host "是否同时安装可选的 SteelSeries GG/Sonar 降噪功能？(y/N)"
if ($installSonar -match '^(y|yes)$') {
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        Write-Host "未找到 winget；可稍后从 https://steelseries.com/gg 手动安装 Sonar。" -ForegroundColor Yellow
    } else {
        winget install --id SteelSeries.GG -e --accept-package-agreements --accept-source-agreements
        if ($LASTEXITCODE -ne 0) { throw "SteelSeries GG 安装失败，退出代码：$LASTEXITCODE" }
    }
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  安装程序已结束。请完成以下设备配置：" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "1. 在 Equalizer APO Device Selector -> Capture devices 中勾选要处理的麦克风（若使用 Sonar，选 Sonar - Microphone）。"
Write-Host "2. 应用更改并按提示重启 Windows；APO 配置目录只会在安装后创建。"
Write-Host "3. MiniVoice 还需要兼容的 64 位 VST2 变声插件 DLL；本包目前不含该 DLL。"
Write-Host "4. 安装完成并重启后，再启动 MiniVoice 并配置 VST 插件。"
Write-Host ""
Pause
