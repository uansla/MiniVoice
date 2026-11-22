#Requires -RunAsAdministrator
<#
.SYNOPSIS
    初始化 Equalizer APO 配置目录权限并挂载 极简变声 (MiniVoice) 路由文件。
    运行一次后，后续双击 run.bat 即可无需每次弹窗请求管理员权限直接热切换变声。
#>

$ApoConfigDir = "C:\Program Files\EqualizerAPO\config"
$MainConfig = Join-Path $ApoConfigDir "config.txt"
$HookFile = Join-Path $ApoConfigDir "minivoice.txt"

if (-not (Test-Path $ApoConfigDir)) {
    Write-Host "[错误] 未找到 Equalizer APO 目录：$ApoConfigDir" -ForegroundColor Red
    Write-Host "请先运行 scripts\install_tools.ps1 安装 Equalizer APO。" -ForegroundColor Yellow
    Pause
    exit 1
}

Write-Host "[1/3] 正在为当前用户授予 Equalizer APO config 目录的写入权限..." -ForegroundColor Green
$CurrentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
icacls $ApoConfigDir /grant "${CurrentUser}:(OI)(CI)M" /T | Out-Null

Write-Host "[2/3] 正在创建初始路由文件 minivoice.txt..." -ForegroundColor Green
if (-not (Test-Path $HookFile)) {
    Set-Content -Path $HookFile -Value "# [MiniVoice-AutoManaged]`nDevice: SteelSeries Sonar - Microphone`nStage: capture`n" -Encoding UTF8
}

Write-Host "[3/3] 正在检查并挂载至主 config.txt..." -ForegroundColor Green
$Content = if (Test-Path $MainConfig) { Get-Content -Path $MainConfig -Raw -Encoding UTF8 } else { "" }
if ($Content -notmatch "minivoice\.txt") {
    if (Test-Path $MainConfig) {
        $Backup = Join-Path $ApoConfigDir ("config.backup." + (Get-Date -Format "yyyyMMdd_HHmmss") + ".txt")
        Copy-Item -Path $MainConfig -Destination $Backup
        Write-Host "  已备份原配置至：$Backup" -ForegroundColor DarkGray
    }
    Add-Content -Path $MainConfig -Value "`n# [MiniVoice-AutoManaged]`nInclude: minivoice.txt`n" -Encoding UTF8
    Write-Host "  挂载成功！" -ForegroundColor Green
} else {
    Write-Host "  已挂载过，无需重复操作。" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "初始化完成！现在可以直接双击根目录的 run.bat 启动极简变声 (MiniVoice)。" -ForegroundColor Cyan
Pause
