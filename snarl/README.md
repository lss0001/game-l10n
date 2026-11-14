# Snarl 简体中文汉化补丁

《Snarl》（v1.0.3）的民间简体中文汉化，共 **1,641 条**词条，含配套中文像素字体。

> 本仓库不包含游戏本体，也不包含游戏数据或修改后的 exe。

## 和 Lamplight City 补丁的区别

Snarl 原版使用 **AGS 3.6.2** 引擎，不支持中文字体和 UTF-8 文本。

所以这个补丁不能只替换翻译文件，**必须把引擎换成 AGS 3.6.3**，再套用中文字体替换。

为此本仓库提供 `patch_snarl_engine.py`：在你自己的电脑上，用原版游戏 + 官方 AGS 3.6.3 引擎合成汉化版 exe，**不涉及任何游戏数据的再分发**。

## 安装

### 1. 准备

- 正版 Snarl 1.0.3（含 `Snarl.exe`）
- AGS 3.6.3 引擎的 `acwin.exe`
  - 下载：https://github.com/adventuregamestudio/ags/releases
  - 找 3.6.3.x 的 Windows 发布包，解压后里面有 `acwin.exe`

### 2. 合成

在本目录打开 PowerShell：

```powershell
python patch_snarl_engine.py `
  --game "D:\Games\Snarl 1.0.3" `
  --engine "D:\AGS\acwin.exe" `
  --out  "D:\Games\Snarl 汉化版"
```

生成的文件：

```
Snarl 汉化版/
├── Snarl.exe        ← 3.6.3 引擎 + 原版数据
├── Snarl.tra        ← 中文翻译（含字体替换指令）
├── zh.ttf           ← 中文像素字体
├── acsetup.cfg      ← 已设置 translation=Snarl
├── SDL2.dll / audio.vox / winsetup.exe（从原版复制）
```

### 3. 运行

双击 `Snarl 汉化版/Snarl.exe`。

想改窗口模式：运行 `winsetup.exe`。

## 卸载

直接删掉汉化版整个文件夹即可，原版游戏不受影响。

## 字体

- [Fusion Pixel Font](https://github.com/TakWolf/fusion-pixel-font) 12px，SIL OFL 1.1
- 许可全文见 `fonts/LICENSE-OFL.txt`

## 许可与免责

- 汉化文本：CC BY-NC-SA 4.0，禁止商业使用
- 字体：SIL OFL 1.1
- 游戏版权归 Beyond Booleans / Yanek_Crispbread 所有
- 本补丁与原作者无关；请支持正版

## 致谢

- Beyond Booleans / Yanek_Crispbread：原作
- Adventure Game Studio：引擎
- TakWolf：Fusion Pixel 字体
