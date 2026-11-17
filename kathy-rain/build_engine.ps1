# Kathy Rain 中文版构建脚本
#
# 用法：
#   powershell -ExecutionPolicy Bypass -File build_engine.ps1 `
#       -GameDir "C:\Program Files (x86)\Steam\steamapps\common\Kathy Rain" `
#       -WorkDir "D:\kr-build"
#
# 需要：gh、python、cmake、ninja、7z、VS Build Tools(x86)

param(
    [Parameter(Mandatory = $true)][string]$GameDir,
    [string]$WorkDir = "D:\kr-build",
    [string]$VcVars = "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars32.bat",
    [string]$SevenZip = "C:\Program Files\7-Zip\7z.exe"
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot

function Step($msg) { Write-Host "== $msg" -ForegroundColor Cyan }
function Need($path, $what) { if (-not (Test-Path $path)) { throw "缺少 $what : $path" } }

Need $GameDir "游戏目录"
Need (Join-Path $GameDir "KathyRain.exe") "原版 KathyRain.exe"
Need $VcVars "vcvars32.bat"
Need $SevenZip "7z.exe"

New-Item -ItemType Directory -Force $WorkDir | Out-Null
Push-Location $WorkDir
try {
    Step "1/8 下载 AGS 3.6.3.15 源码与依赖"
    if (-not (Test-Path "ags_3.6.3.15_source.zip")) {
        gh release download v3.6.3.15 --repo adventuregamestudio/ags --pattern "ags_3.6.3.15_source.zip" --clobber
    }
    if (-not (Test-Path "WinDevDependenciesVS.zip")) {
        gh release download v3.6.3.15 --repo adventuregamestudio/ags --pattern "WinDevDependenciesVS.zip" --clobber
    }
    if (-not (Test-Path "src")) { Expand-Archive "ags_3.6.3.15_source.zip" -DestinationPath "src" -Force }
    if (-not (Test-Path "deps")) { Expand-Archive "WinDevDependenciesVS.zip" -DestinationPath "deps" -Force }

    $src = Join-Path $WorkDir "src\ags_3.6.3.15_source"
    Need $src "AGS 源码"

    Step "2/8 准备 ogg / vorbis 源码"
    if (-not (Test-Path "libogg-1.3.5")) {
        if (-not (Test-Path "libogg-1.3.5.tar.xz")) {
            gh release download v1.3.5 --repo xiph/ogg --pattern "libogg-1.3.5.tar.xz" --clobber
        }
        & $SevenZip x "libogg-1.3.5.tar.xz" -o. -y | Out-Null
        & $SevenZip x "libogg-1.3.5.tar" -o. -y | Out-Null
    }
    if (-not (Test-Path "libvorbis-1.3.7")) {
        if (-not (Test-Path "libvorbis-1.3.7.tar.xz")) {
            gh release download v1.3.7 --repo xiph/vorbis --pattern "libvorbis-1.3.7.tar.xz" --clobber
        }
        & $SevenZip x "libvorbis-1.3.7.tar.xz" -o. -y | Out-Null
        & $SevenZip x "libvorbis-1.3.7.tar" -o. -y | Out-Null
    }

    Step "3/8 改写 CMake FetchOgg / FetchVorbis"
    @"
set(ogg_content_SOURCE_DIR "$($WorkDir.Replace('\','/'))/libogg-1.3.5")
set(ogg_content_BINARY_DIR "`${CMAKE_BINARY_DIR}/ogg_content-build")
file(COPY `${CMAKE_SOURCE_DIR}/Engine/libsrc/ogg/CMakeLists.txt DESTINATION `${ogg_content_SOURCE_DIR})
add_subdirectory(`${ogg_content_SOURCE_DIR} `${ogg_content_BINARY_DIR} EXCLUDE_FROM_ALL)
set(OGG_LIBRARIES Ogg::Ogg)
"@ | Set-Content (Join-Path $src "CMake\FetchOgg.cmake") -Encoding UTF8
    @"
set(vorbis_content_SOURCE_DIR "$($WorkDir.Replace('\','/'))/libvorbis-1.3.7")
set(vorbis_content_BINARY_DIR "`${CMAKE_BINARY_DIR}/vorbis_content-build")
file(COPY `${CMAKE_SOURCE_DIR}/Engine/libsrc/vorbis/CMakeLists.txt DESTINATION `${vorbis_content_SOURCE_DIR})
add_subdirectory(`${vorbis_content_SOURCE_DIR} `${vorbis_content_BINARY_DIR} EXCLUDE_FROM_ALL)
set(VORBIS_LIBRARIES Vorbis::Vorbis)
"@ | Set-Content (Join-Path $src "CMake\FetchVorbis.cmake") -Encoding UTF8

    Step "4/8 应用汉化补丁"
    python (Join-Path $repo "tools\apply_engine_patches.py") $src
    if ($LASTEXITCODE -ne 0) { throw "补丁脚本失败" }

    Step "5/8 配置与编译"
    $envOut = cmd /c "`"$VcVars`" >nul 2>&1 && set"
    foreach ($line in $envOut) {
        if ($line -match "^([^=]+)=(.*)$") { [Environment]::SetEnvironmentVariable($matches[1], $matches[2]) }
    }
    $apeg = Join-Path $src "Engine\libsrc\apeg-1.2.1"
    $build = Join-Path $WorkDir "build"
    cmake -G Ninja -S $src -B $build `
        -DCMAKE_BUILD_TYPE=RelWithDebInfo `
        -DAGS_BUILTIN_PLUGINS=ON `
        -DAGS_NO_VIDEO_PLAYER=ON `
        -DSDLSOUND_DECODER_VORBIS=ON `
        "-DCMAKE_C_FLAGS=/I$apeg" `
        "-DCMAKE_CXX_FLAGS=/I$apeg" `
        "-DCMAKE_PREFIX_PATH=$($WorkDir.Replace('\','/'))/deps"
    if ($LASTEXITCODE -ne 0) { throw "CMake 配置失败" }
    cmake --build $build --parallel 8
    if ($LASTEXITCODE -ne 0) { throw "编译失败" }

    Step "6/8 合成 exe"
    $outDir = Join-Path $WorkDir "out"
    New-Item -ItemType Directory -Force $outDir | Out-Null
    $orig = Join-Path $GameDir "KathyRain.exe.orig"
    if (-not (Test-Path $orig)) { Copy-Item (Join-Path $GameDir "KathyRain.exe") $orig -Force }
    python (Join-Path $repo "tools\pack_engine.py") $orig (Join-Path $build "ags.exe") (Join-Path $outDir "KathyRain.exe")
    if ($LASTEXITCODE -ne 0) { throw "打包失败" }

    Step "7/8 生成翻译文件"
    $env:KR_FONT_IDS = "18,19"
    python (Join-Path $repo "source\build_tra.py") (Join-Path $outDir "简体中文.tra") 12
    if ($LASTEXITCODE -ne 0) { throw "生成 tra 失败" }

    Step "8/8 组装游戏目录"
    Copy-Item (Join-Path $outDir "KathyRain.exe") $GameDir -Force
    Copy-Item (Join-Path $outDir "简体中文.tra") $GameDir -Force
    Copy-Item (Join-Path $repo "fonts\zh.ttf") $GameDir -Force
    Copy-Item (Join-Path $repo "acsetup.cfg") $GameDir -Force

    Write-Host ""
    Write-Host "完成。请按 VERIFY.md 验证。" -ForegroundColor Green
    Write-Host "游戏目录: $GameDir"
}
finally {
    Pop-Location
}
