# Snarl 汉化安装校验
#
# 用法：
#   powershell -ExecutionPolicy Bypass -File verify_setup.ps1 `
#       -GameDir "D:\Games\Snarl 汉化版"

param(
    [Parameter(Mandatory = $true)][string]$GameDir
)

$ErrorActionPreference = "Continue"
$fail = 0
function Ok($m)   { Write-Host "  OK   $m" -ForegroundColor Green }
function Bad($m)  { Write-Host "  FAIL $m" -ForegroundColor Red; $script:fail++ }
function Info($m) { Write-Host "  --   $m" -ForegroundColor DarkGray }

Write-Host "游戏目录: $GameDir"
if (-not (Test-Path $GameDir)) { throw "目录不存在" }

# 1. exe
$exe = Join-Path $GameDir "Snarl.exe"
if (Test-Path $exe) {
    $len = (Get-Item $exe).Length
    if ($len -gt 50MB) { Ok "Snarl.exe 存在（$len 字节）" }
    else { Bad "Snarl.exe 偏小（$len），可能不是合成后的 exe" }
}
else { Bad "缺少 Snarl.exe" }

# 2. 翻译与字体
$tra = Join-Path $GameDir "Snarl.tra"
if (Test-Path $tra) {
    $len = (Get-Item $tra).Length
    if ($len -gt 100000) { Ok "Snarl.tra 存在（$len 字节）" }
    else { Bad "Snarl.tra 偏小（$len）" }
}
else { Bad "缺少 Snarl.tra" }

$font = Join-Path $GameDir "zh.ttf"
if (Test-Path $font) { Ok "zh.ttf 存在" } else { Bad "缺少 zh.ttf" }

# 3. 配置
$cfg = Join-Path $GameDir "acsetup.cfg"
if (Test-Path $cfg) {
    $text = Get-Content $cfg -Raw
    if ($text -match "(?m)^\s*translation\s*=\s*Snarl\s*$") { Ok "acsetup.cfg translation=Snarl" }
    else { Bad "acsetup.cfg 未设置 translation=Snarl" }
}
else { Bad "缺少 acsetup.cfg" }

# 4. 日志
$log = Join-Path $GameDir "logs\ags.log"
if (Test-Path $log) {
    $hit = Select-String -Path $log -Pattern "Translation loaded: .*tra" | Select-Object -Last 1
    if ($hit) { Ok "日志: $($hit.Line.Trim())" } else { Info "日志中没有 Translation loaded（先启动一次）" }
}
else { Info "还没有 logs\\ags.log（先启动一次）" }

Write-Host ""
if ($fail -eq 0) { Write-Host "校验通过。" -ForegroundColor Green; exit 0 }
else { Write-Host "有 $fail 项失败，见上方 FAIL。" -ForegroundColor Red; exit 1 }
