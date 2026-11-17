# Kathy Rain 汉化安装校验
#
# 用法：
#   powershell -ExecutionPolicy Bypass -File verify_setup.ps1 `
#       -GameDir "C:\Program Files (x86)\Steam\steamapps\common\Kathy Rain"

param(
    [Parameter(Mandatory = $true)][string]$GameDir,
    [string]$OrigExe = "KathyRain.exe.orig"
)

$ErrorActionPreference = "Continue"
$fail = 0

function Ok($msg)   { Write-Host "  OK   $msg" -ForegroundColor Green }
function Bad($msg)  { Write-Host "  FAIL $msg" -ForegroundColor Red; $script:fail++ }
function Info($msg) { Write-Host "  --   $msg" -ForegroundColor DarkGray }

Write-Host "游戏目录: $GameDir"
if (-not (Test-Path $GameDir)) { throw "目录不存在" }

# 1. 原版 exe
$orig = Join-Path $GameDir $OrigExe
if (Test-Path $orig) {
    $len = (Get-Item $orig).Length
    if ($len -eq 197487159) { Ok "原版 exe 大小 197,487,159" }
    else { Bad "原版 exe 大小 $len，预期 197,487,159" }

    $bytes = [IO.File]::ReadAllBytes($orig)
    if ($bytes.Length -gt 2146816) {
        $tail = $bytes[-4..-1]
        if ([Text.Encoding]::ASCII.GetString($tail) -eq "SIGE") { Ok "数据包尾部标记 SIGE" }
        else { Bad "数据包尾部标记不是 SIGE" }
    }
}
else { Info "未找到 $OrigExe（如果已保留原版备份可忽略）" }

# 2. 当前 exe
$exe = Join-Path $GameDir "KathyRain.exe"
if (Test-Path $exe) {
    $len = (Get-Item $exe).Length
    if ($len -gt 198MB) { Ok "当前 exe 存在（$len 字节）" }
    else { Bad "当前 exe 偏小（$len），可能还是原版" }

    $fs = [IO.File]::OpenRead($exe)
    try {
        $fs.Seek(-16, [IO.SeekOrigin]::End) | Out-Null
        $buf = New-Object byte[] 4
        $fs.Read($buf, 0, 4) | Out-Null
        $engineLen = [BitConverter]::ToInt32($buf, 0)
        if ($engineLen -gt 2MB -and $engineLen -lt 20MB) { Ok "引擎长度字段 = $engineLen" }
        else { Bad "引擎长度字段异常：$engineLen（可能写错位置）" }
    }
    finally { $fs.Close() }
}
else { Bad "缺少 KathyRain.exe" }

# 3. 翻译与字体
$tra = Join-Path $GameDir "简体中文.tra"
if (Test-Path $tra) {
    $len = (Get-Item $tra).Length
    if ($len -gt 400000) { Ok "简体中文.tra 存在（$len 字节）" }
    else { Bad "简体中文.tra 偏小（$len），可能未生成完整" }
}
else { Bad "缺少 简体中文.tra" }

$font = Join-Path $GameDir "zh.ttf"
if (Test-Path $font) { Ok "zh.ttf 存在" } else { Bad "缺少 zh.ttf" }

# 4. 配置
$cfg = Join-Path $GameDir "acsetup.cfg"
if (Test-Path $cfg) {
    $text = Get-Content $cfg -Raw
    if ($text -match "(?m)^\s*translation\s*=\s*简体中文\s*$") { Ok "acsetup.cfg translation=简体中文" }
    else { Bad "acsetup.cfg 未设置 translation=简体中文" }
}
else { Bad "缺少 acsetup.cfg" }

# 5. 日志
$log = Join-Path $GameDir "logs\ags.log"
if (Test-Path $log) {
    $hit = Select-String -Path $log -Pattern "Translation loaded: .*tra" | Select-Object -Last 1
    if ($hit) { Ok "日志: $($hit.Line.Trim())" } else { Info "日志中没有 Translation loaded（先启动一次游戏）" }
}
else { Info "还没有 logs\\ags.log（先启动一次游戏）" }

Write-Host ""
if ($fail -eq 0) { Write-Host "校验通过。" -ForegroundColor Green; exit 0 }
else { Write-Host "有 $fail 项失败，见上方 FAIL。" -ForegroundColor Red; exit 1 }
