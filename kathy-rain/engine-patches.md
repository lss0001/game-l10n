# 引擎补丁说明（AGS 3.6.3.15）

本汉化使用自编译的 AGS 3.6.3.15 引擎，原因：

1. 原版 3.3.0.1150 不支持 UTF-8 + TTF 中文字体
2. 3.6 的若干行为与老游戏不一致，需要兼容补丁

以下补丁都以 `loaded_game_file_version < kGameVersion_350`（即老游戏）为条件，只影响本作。

## 1. 中文字体回退

`Common/font/fonts.cpp`

- 新增 `has_high_bytes()` 判断文本是否含高位字节
- `wouttextxy`、`get_text_width`、`get_text_height`、`get_text_width_outlined` 中：
  含高位字节的文本强制使用 19 号字体渲染

```cpp
if (font_number != 19 && has_high_bytes(texx) && fonts.size() > 19 && fonts[19].Renderer)
    font_number = 19;
```

## 2. 轮盘动作文字（悬停判定）

`Engine/ac/button.cpp` → `Button_GetGraphic`

老游戏的脚本通过比较 `btn.Graphic == btn.MouseOverGraphic` 判断悬停。3.6 改用控件悬停状态，老游戏因此拿不到 MouseOver 图。

补丁：按屏幕坐标 + GUI 位置计算鼠标是否落在按钮矩形内，命中则返回 MouseOver 图。

`Engine/main/game_run.cpp` → GUI 轮询

老游戏 GUI 未设置 `Clickable`，3.6 会跳过轮询：

```cpp
const bool legacy = loaded_game_file_version < kGameVersion_350;
if (!legacy && !gui.IsClickable()) continue;
const bool focus = legacy ? gui.GetRect().IsInside(mousex, mousey) : (focused_gui == gui.GetID());
gui.Poll(mousex, mousey, focus);
```

## 3. 0xB3 撇号修正

`Engine/ac/label.cpp` → `Label_SetText`

游戏数据里部分字符串用 `0xB3`（cp1252 的 `³`）代替撇号，导致：

- 词表显示 `IT3S`
- 与脚本字面量 `IT'S` 做 `IndexOf` 匹配失败

补丁：设置文本时把 `0xB3` 与 UTF-8 序列 `C2 B3` 统一替换为 `'`，缓冲区用 8192 防止截断。

## 4. String.Substring 越界钳制

`Engine/ac/string.cpp` → `String_Substring`

`Notebook.asc` 会用 `Substring(8, len - 8)` 去掉笔记前缀，标题短于 8 字符时越界崩溃。

补丁：越界时钳制 index/length，返回空串或可截取部分，而不是 `quit`。

## 5. 老游戏对象点击容错（已移除）

曾尝试给老游戏的对象像素命中加 6~8 像素矩形兜底，但会导致人物抢走背后血墙的点击，已回滚，不包含在最终版中。

## 6. 老游戏 GUI 点击兜底（已移除）

曾为“X 按钮所在 GUI 被标为不可点击”加过“按 GUI 矩形范围兜底”的命中，副作用是轮盘 GUI 会吃掉所有场景点击，已回滚。

## 7. 视频模块空实现

`Engine/media/video/video.cpp` 增加 `video_single_pause/resume` 空实现，用于在未启用 Theora 的情况下完成编译；不影响游戏（本作无视频）。

## 构建要点

- 源码：AGS 3.6.3.15
- 依赖：WinDevDependenciesVS（SDL2 / SDL_sound / Xiph）
- ogg / vorbis 源码本地化（CMake FetchContent 改为本地目录）
- 配置：`RelWithDebInfo`、`AGS_BUILTIN_PLUGINS=ON`、`AGS_NO_VIDEO_PLAYER=ON`、`SDLSOUND_DECODER_VORBIS=ON`

## 打包 exe

```
新 exe = 编译出的引擎 + 原版 exe 中从偏移 2146816 开始的数据
最后 16 字节处写入 4 字节引擎长度（不是 20 字节，也不能覆盖数据）
```

错误写法（会写坏数据包尾部目录，导致 `room40.crm` 读取失败）：
在文件末尾 `-20` 处写 8 字节长度，或直接覆盖原数据尾部。
