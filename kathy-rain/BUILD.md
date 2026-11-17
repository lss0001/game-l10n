# 从零构建可运行的中文版

本文假设你只有：

- Windows 10/11
- Steam 正版《Kathy Rain》
- 本仓库

目标：得到 `KathyRain.exe`（中文引擎 + 原版数据）+ `简体中文.tra` + `zh.ttf`，可直接启动。

## 0. 你需要准备的工具

| 工具 | 用途 | 备注 |
|---|---|---|
| Visual Studio Build Tools（含 C++ x86） | 编译引擎 | 需要 `vcvars32.bat` |
| CMake ≥ 3.21 | 配置工程 | 命令行可用即可 |
| Ninja | 构建 | 与 CMake 搭配 |
| Python 3.8+ | 生成 tra / 打补丁 / 打包 | 无第三方依赖 |
| Git / GitHub CLI | 下载源码与依赖 | 可选，能手动下载也行 |
| 7-Zip | 解压 tar.xz | 解压 ogg/vorbis 源码用 |

下文以 PowerShell 为例。

## 1. 准备原版游戏

从 Steam 安装游戏，确认目录中有：

```
KathyRain.exe        197,487,159 字节
audio.vox
speech.vox
```

建议先把原版 exe 备份为 `KathyRain.exe.orig`。

`KathyRain.exe.orig` 的校验点：

- 大小：`197,487,159`
- 游戏数据起始偏移：`2,146,816`
- 文件末尾 4 字节：`SIGE`

用 `verify_setup.ps1` 可以自动检查这些。

## 2. 下载 AGS 3.6.3.15 源码与依赖

```powershell
$work = "D:\kr-build"
New-Item -ItemType Directory -Force $work | Out-Null
cd $work

gh release download v3.6.3.15 --repo adventuregamestudio/ags `
  --pattern "ags_3.6.3.15_source.zip" --clobber
gh release download v3.6.3.15 --repo adventuregamestudio/ags `
  --pattern "WinDevDependenciesVS.zip" --clobber

Expand-Archive ags_3.6.3.15_source.zip -DestinationPath src -Force
Expand-Archive WinDevDependenciesVS.zip -DestinationPath deps -Force
```

解压后应得到：

```
D:\kr-build\src\ags_3.6.3.15_source\
D:\kr-build\deps\SDL2\
D:\kr-build\deps\SDL_sound\
D:\kr-build\deps\Xiph\
```

## 3. 准备 ogg / vorbis 源码（离线）

AGS 的 CMake 默认会联网下载 ogg/vorbis。网络不通时会失败，所以手动放到本地：

```powershell
gh release download v1.3.5 --repo xiph/ogg --pattern "libogg-1.3.5.tar.xz" --clobber
gh release download v1.3.7 --repo xiph/vorbis --pattern "libvorbis-1.3.7.tar.xz" --clobber

7z x libogg-1.3.5.tar.xz -o. -y
7z x libogg-1.3.5.tar -o. -y
7z x libvorbis-1.3.7.tar.xz -o. -y
7z x libvorbis-1.3.7.tar -o. -y
```

得到 `D:\kr-build\libogg-1.3.5\` 和 `D:\kr-build\libvorbis-1.3.7\`。

## 4. 让 CMake 使用本地 ogg/vorbis

编辑：

```
src\ags_3.6.3.15_source\CMake\FetchOgg.cmake
src\ags_3.6.3.15_source\CMake\FetchVorbis.cmake
```

`FetchOgg.cmake` 整个替换为：

```cmake
set(ogg_content_SOURCE_DIR "D:/kr-build/libogg-1.3.5")
set(ogg_content_BINARY_DIR "${CMAKE_BINARY_DIR}/ogg_content-build")
file(COPY ${CMAKE_SOURCE_DIR}/Engine/libsrc/ogg/CMakeLists.txt DESTINATION ${ogg_content_SOURCE_DIR})
add_subdirectory(${ogg_content_SOURCE_DIR} ${ogg_content_BINARY_DIR} EXCLUDE_FROM_ALL)
set(OGG_LIBRARIES Ogg::Ogg)
```

`FetchVorbis.cmake` 整个替换为：

```cmake
set(vorbis_content_SOURCE_DIR "D:/kr-build/libvorbis-1.3.7")
set(vorbis_content_BINARY_DIR "${CMAKE_BINARY_DIR}/vorbis_content-build")
file(COPY ${CMAKE_SOURCE_DIR}/Engine/libsrc/vorbis/CMakeLists.txt DESTINATION ${vorbis_content_SOURCE_DIR})
add_subdirectory(${vorbis_content_SOURCE_DIR} ${vorbis_content_BINARY_DIR} EXCLUDE_FROM_ALL)
set(VORBIS_LIBRARIES Vorbis::Vorbis)
```

## 5. 应用汉化补丁

```powershell
python tools\apply_engine_patches.py D:\kr-build\src\ags_3.6.3.15_source
```

脚本会依次修改：

- 中文字体回退（fonts.cpp）
- 老游戏 GUI 轮询（game_run.cpp）
- 轮盘按钮悬停（button.cpp）
- 撇号修正（label.cpp）
- Substring 越界钳制（string.cpp）
- 视频空实现（video.cpp）

## 6. 配置与编译

```powershell
cmd /c "`"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars32.bat`" && set" |
  ForEach-Object { if ($_ -match '^([^=]+)=(.*)$') { [Environment]::SetEnvironmentVariable($matches[1],$matches[2]) } }

cmake -G Ninja -S D:\kr-build\src\ags_3.6.3.15_source -B D:\kr-build\build `
  -DCMAKE_BUILD_TYPE=RelWithDebInfo `
  -DAGS_BUILTIN_PLUGINS=ON `
  -DAGS_NO_VIDEO_PLAYER=ON `
  -DSDLSOUND_DECODER_VORBIS=ON `
  "-DCMAKE_C_FLAGS=/ID:/kr-build/src/ags_3.6.3.15_source/Engine/libsrc/apeg-1.2.1" `
  "-DCMAKE_CXX_FLAGS=/ID:/kr-build/src/ags_3.6.3.15_source/Engine/libsrc/apeg-1.2.1" `
  "-DCMAKE_PREFIX_PATH=D:/kr-build/deps"

cmake --build D:\kr-build\build --parallel 8
```

产物：`D:\kr-build\build\ags.exe`

### 编译常见错误

| 错误 | 处理 |
|---|---|
| `apeg.h: No such file` | 确认上面的 `CMAKE_C_FLAGS` 包含 apeg 目录 |
| `HError` / `String` 未声明 | 确认 `video.cpp` 已加 `util/error.h`、`videoplayer.h` 与命名空间限定（补丁脚本已处理） |
| `video_single_pause` 链接失败 | 补丁脚本会在 `video.cpp` 追加空实现 |
| `ogg/ogg.h: No such file` | 第 3、4 步没做对，或 `ogg` 头文件目录不在 include 路径 |
| FetchContent 联网失败 | 第 4 步的本地替换没生效 |

## 7. 合成可运行的 exe

**这一步决定 40 号房间会不会黑屏。**

```powershell
python tools\pack_engine.py `
  "C:\Program Files (x86)\Steam\steamapps\common\Kathy Rain\KathyRain.exe.orig" `
  D:\kr-build\build\ags.exe `
  D:\kr-build\out\KathyRain.exe
```

脚本会：

1. 写入自编译引擎
2. 追加原版游戏数据（从偏移 2,146,816 开始）
3. 在文件末尾 **-16** 处写入 4 字节引擎长度
4. 校验 `SIGE` 标记与长度字段

> 不要用“末尾 -20 写 8 字节”的常见做法，那会覆盖数据包尾部目录，导致 `room40.crm` 读取失败（黑屏/卡死）。

## 8. 生成翻译文件

仓库已带生成好的 `简体中文.tra`。需要修改译文时：

```powershell
$env:KR_FONT_IDS = "18,19"
python source\build_tra.py 简体中文.tra 12
```

- `KR_FONT_IDS`：要覆盖为中文的字体编号
- 第二个参数：字号（12 为最终采用值）

输入文件：

- `source/source.json`：原文对照
- `source/manual.json`：人工校对译文（优先）
- `source/extra_keys.json`：额外字面量键

## 9. 组装游戏目录

```
Kathy Rain\
  KathyRain.exe          ← 第 7 步产物
  简体中文.tra
  zh.ttf
  acsetup.cfg            ← 用仓库的样例，确认 translation=简体中文
  audio.vox / speech.vox ← 原版文件
```

启动后按 `VERIFY.md` 逐项检查。

## 10. 卸载 / 回滚

把 `KathyRain.exe.orig` 改回 `KathyRain.exe`，删除 `简体中文.tra`、`zh.ttf`，`acsetup.cfg` 中 `translation=` 清空即可。
