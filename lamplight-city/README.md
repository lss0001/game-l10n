# Lamplight City 简体中文补丁

把《Lamplight City》（灯火之城）的英文文本替换为简体中文的民间汉化补丁。

适用于 Steam 正版 1.13 版（AGS 3.6.0.58），包含 **10,720 条翻译**和一个配套的中文像素字体。

> 本仓库不包含游戏本体。请先购买正版。

装完想逐项检查：见 [VERIFY.md](VERIFY.md)，或运行 `verify_setup.ps1`。
配置可直接参考 [acsetup.cfg](acsetup.cfg)（`translation=Deutsch`）。

## 这个补丁包含什么

- `German.tra`：中文翻译文件（游戏通过“德语”位置加载它）
- `fonts/zh.ttf`：开源像素中文字体（Fusion Pixel）
- 说明文档与许可

汉化范围：主线剧情、支线、对话选项、物品描述、案件档案与界面文本。

## 安装前需要知道的一件事

游戏本身只有 **English（英语）** 和 **Deutsch（德语）** 两个语言位置，没有“中文”这个选项。

所以汉化补丁的做法是：**把中文放进德语的位置**。

安装完成后，在游戏里把语言选成 **Deutsch（德语）**，看到的就会是中文。选 English 仍然是英文。

## 安装

1. 打开游戏目录：`steamapps\common\Lamplight City`
2. 备份原文件：把 `German.tra` 改名为 `German.tra.orig`
3. 把本仓库的 `German.tra` 复制进去
4. 把 `fonts/zh.ttf` 复制 8 份，分别命名为：
   ```
   agsfnt0.ttf  agsfnt1.ttf  agsfnt2.ttf  agsfnt3.ttf
   agsfnt4.ttf  agsfnt5.ttf  agsfnt6.ttf  agsfnt7.ttf
   ```
   全部放进游戏目录
5. 启动游戏，打开 `Settings`（设置）
6. 把 `Language`（语言）切换为 **Deutsch**
7. 重启游戏

## 常见问题

**进游戏还是英文？**

- 检查 `Settings → Language` 是不是 **Deutsch**，改完要重启游戏
- 确认 `German.tra` 是补丁里的这份（约 1.3 MB，原版是 1.45 MB）
- 确认 `agsfnt0.ttf` ~ `agsfnt7.ttf` 都在游戏目录里

**游戏里切换语言没反应？**

可以在游戏目录用记事本打开 `acsetup.cfg`，找到：

```
[language]
translation=
```

改成：

```
[language]
translation=German
```

保存后重启游戏。

**书页、报纸、信件里的英文**

这些是画在图片里的美术资源，翻译文件改不了，无法汉化。

**设置菜单里的英文/德文**

同样是图片，属于正常现象。

## 卸载

1. 删除游戏目录里的 `agsfnt0.ttf` ~ `agsfnt7.ttf`
2. 把 `German.tra.orig` 改回 `German.tra`
3. 游戏里把语言切回 English

## 字体

- [Fusion Pixel Font](https://github.com/TakWolf/fusion-pixel-font) by TakWolf，SIL Open Font License 1.1
- 许可全文见 `fonts/LICENSE-OFL.txt`

## 许可与免责

- 汉化文本：CC BY-NC-SA 4.0，禁止商业使用
- 字体：SIL OFL 1.1
- 本补丁与游戏作者、发行商无关；请支持正版
- 使用本补丁造成的任何问题由使用者自行承担

## 致谢

- Francisco Gonzalez / Grundislav Games：原作
- Application Systems Heidelberg：官方德语本地化
- TakWolf：Fusion Pixel 字体
