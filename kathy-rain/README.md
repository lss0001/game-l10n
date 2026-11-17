# Kathy Rain 简体中文汉化

把《Kathy Rain》（凯西·雷恩）的英文文本替换为简体中文的民间汉化补丁。

适用于 Steam 正版（AppID `370910`）。包含 **4,688 条翻译** 和一个配套的中文像素字体。

> 本仓库不包含游戏本体。请先购买正版。

## 快速开始

- 想直接装：看下面的「安装」
- 想从源码编译引擎：看 [BUILD.md](BUILD.md)
- 装完想逐项检查：看 [VERIFY.md](VERIFY.md)

仓库内提供的脚本：

```
build_engine.ps1          一键下载源码/依赖 → 应用补丁 → 编译 → 合成 exe → 生成 tra
verify_setup.ps1          校验原版 exe、数据偏移、tra、字体、配置与日志
tools/apply_engine_patches.py   给 AGS 3.6.3.15 源码打补丁
tools/pack_engine.py            正确合成 exe（修复 40 号房间黑屏）
source/build_tra.py             从译文工程生成 .tra
acsetup.cfg                     可直接复制的配置样例
```

## 这个补丁包含什么

- `简体中文.tra`：中文翻译文件（AGS 翻译格式，UTF-8）
- `fonts/zh.ttf`：开源像素中文字体（Zpix，SIL OFL 1.1）
- `source/`：翻译工程文件（原文、人工校对、生成脚本）
- `engine-patches.md`：引擎补丁说明（中文显示、动作文字、兼容修复）

汉化范围：主线剧情、对话、物品与热点名称、轮盘动作文字、笔记本、电话簿、电脑界面、结局字幕。

## 安装前需要知道的一件事

原版引擎是 **AGS 3.3.0.1150**，**不支持** UTF-8 + TTF 中文字体。

所以这个汉化不能只替换 `.tra`，还需要一个 **AGS 3.6.3.15 自编译引擎**（带中文字体回退和几处老游戏兼容补丁）。引擎的修改点、构建参数和打包方式全部写在 `engine-patches.md` 里。

如果你已经有整合好的 `KathyRain.exe`，直接按下面安装即可。

## 安装

1. 打开游戏目录：`steamapps\common\Kathy Rain`
2. 备份原文件：把 `KathyRain.exe` 改名为 `KathyRain.exe.orig`
3. 把整合好的 `KathyRain.exe`（自编译引擎 + 原版数据）放进游戏目录
4. 把本仓库的 `简体中文.tra` 复制进游戏目录
5. 把 `fonts/zh.ttf` 复制进游戏目录（文件名保持 `zh.ttf`）
6. 编辑 `acsetup.cfg`，把语言项改成：

   ```ini
   [language]
   translation=简体中文
   ```

7. 启动游戏，设置里语言应显示「简体中文」

## 常见问题

**进游戏还是英文？**

- 确认 `acsetup.cfg` 里是 `translation=简体中文`
- 确认 `简体中文.tra` 和 `zh.ttf` 都在游戏目录
- 看 `logs\ags.log` 是否有 `Translation loaded: 简体中文.tra`

**文字是方块/空白？**

- 字体没有生效：确认 `zh.ttf` 存在，且引擎是自编译版本（原版 3.3 不支持）

**某个谜题怎么拼都不对？**

以下内容**故意保留英文**，因为游戏用字符串精确匹配：

- VoiceForge 语音拼装谜题
- 冰箱贴拼字：`HOPES IN JAR` / `AN INKIER HEART` / `RULE ME NEMESIS`

**笔记本某行没有电话号码？**

笔记名必须至少 8 个字符，否则脚本 `Substring` 会越界。当前版本已在引擎侧做了越界钳制，但名字过短的行可能不显示号码。

**对话/过场后卡住？**

- 确认没有切出窗口（游戏失焦会暂停）
- 看日志是否重复出现 `Wait` 或停在某个 `Animating` 判断

## 卸载

1. 删除游戏目录里的 `简体中文.tra` 和 `zh.ttf`
2. 把 `KathyRain.exe.orig` 改回 `KathyRain.exe`
3. `acsetup.cfg` 里 `translation=` 清空

## 许可

- 译文：CC BY-NC-SA 4.0（见 `LICENSE.md`）
- 字体 Zpix：SIL OFL 1.1（见 `fonts/LICENSE-OFL.txt`）
- 引擎补丁：Artistic License 2.0（AGS 源码许可）
