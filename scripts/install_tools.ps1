#Requires -RunAsAdministrator
<#
.SYNOPSIS
    极简变声 (MiniVoice) 依赖组件一键安装脚本：
    1. SteelSeries GG (内置免费的 Sonar AI 降噪，屏蔽狗叫/猫叫/键盘声)
    2. Equalizer APO (开源免费的系统级音频处理引擎)
#>

$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  极简变声 (MiniVoice) - 依赖组件一键安装脚本" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host "[错误] 未检测到 winget（Windows 应用安装程序）。" -ForegroundColor Red
    Write-Host "请手动从以下官方地址下载安装：" -ForegroundColor Yellow
    Write-Host "  1. SteelSeries GG: https://steelseries.com/gg"
    Write-Host "  2. Equalizer APO:  https://sourceforge.net/projects/equalizerapo/"
    Pause
    exit 1
}

Write-Host "[1/2] 正在安装 SteelSeries GG (含 Sonar AI 降噪)..." -ForegroundColor Green
winget install --id SteelSeries.GG -e --accept-package-agreements --accept-source-agreements

Write-Host ""
Write-Host "[2/2] 正在安装 Equalizer APO..." -ForegroundColor Green
winget install --id JonasThedering.EqualizerAPO -e --accept-package-agreements --accept-source-agreements

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  基础软件安装完成！接下来的 4 步关键配置：" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "1. 打开 SteelSeries GG -> 启用 Sonar -> Mic 页面选择你的真实麦克风 -> 开启 ClearCast AI Noise Cancellation。"
Write-Host "2. 打开 Equalizer APO 的 Device Selector（设备选择器）-> 切换到 Capture devices（录音设备）-> 勾选 SteelSeries Sonar - Microphone -> 重启电脑。"
Write-Host "3. 将 64 位变声 VST 插件（如 GVST GForm x64 / Graillon Free x64，或经 jBridge 桥接的 RoVee）放入本项目的 vst_plugins 文件夹。"
Write-Host "4. 右键运行 scripts\setup_apo_hook.ps1，随后双击 run.bat 即可启动极简变声！"
Write-Host ""
Pause
