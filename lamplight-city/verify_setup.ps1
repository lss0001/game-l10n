# Lamplight City 汉化安装校验
#
# 用法：
#   powershell -ExecutionPolicy Bypass -File verify_setup.ps1 `
#       -GameDir "C:\Program Files (x86)\Steam\steamapps\common\Lamplight City"

param(
    [Parameter(Mandatory = $true)][string]$GameDir,
    [string]$OrigTra = "German.tra.orig"
)

$ErrorActionPreference = "Continue"
$fail = 0
function Ok($m)   { Write-Host "  OK   $m" -ForegroundColor Green }
function Bad($m)  { Write-Host "  FAIL $m" -ForegroundColor Red; $script:fail++ }
function Info($m) { Write-Host "  --   $m" -ForegroundColor DarkGray }

Write-Host "游戏目录: $GameDir"
if (-not (Test-Path $GameDir)) { throw "目录不存在" }

# 1. 翻译文件
$tra = Join-Path $GameDir "German.tra"
if (Test-Path $tra) {
    $len = (Get-Item $tra).Length
    if ($len -gt 1200000 -and $len -lt 1400000) { Ok "German.tra 大小正常（$len）" }
    else { Bad "German.tra 大小异常（$len），预期约 1.33 MB（补丁版）" }
}
else { Bad "缺少 German.tra" }

if (Test-Path (Join-Path $GameDir $OrigTra)) { Info "已备份原版 $OrigTra" }
else { Info "未发现 $OrigTra（可选）" }

# 2. 中文字体
$missing = @()
0..7 | ForEach-Object {
    $f = Join-Path $GameDir ("agsfnt{0}.ttf" -f $_)
    if (-not (Test-Path $f)) { $missing += "agsfnt$_.ttf" }
}
if ($missing.Count -eq 0) { Ok "agsfnt0.ttf ~ agsfnt7.ttf 齐全" }
else { Bad ("缺少字体: " + ($missing -join ", ")) }

# 3. 配置
$cfg = Join-Path $GameDir "acsetup.cfg"
if (Test-Path $cfg) {
    $text = Get-Content $cfg -Raw
    if ($text -match "(?m)^\s*translation\s*=\s*Deutsch\s*$") { Ok "acsetup.cfg translation=Deutsch" }
    else { Bad "acsetup.cfg 未设置 translation=Deutsch" }
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
