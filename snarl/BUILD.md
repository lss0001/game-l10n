# 从零合成 Snarl 汉化版

本文假设你只有：

- Windows 10/11
- Steam 正版 **Snarl 1.0.3**
- 本仓库

## 0. 原理

Snarl 原版是 **AGS 3.6.2** 编译的，不支持 UTF-8 + TTF 中文字体。

所以不能只替换 `.tra`，必须：

1. 换用 **AGS 3.6.3.15** 引擎
2. 对引擎打三处二进制补丁（否则 3.6.3 跑 3.6.2 游戏会卡死）
3. 用原版数据 + 中文翻译 + 中文字体组装

这些全部由 `patch_snarl_engine.py` 完成，**不涉及游戏数据再分发**。

## 1. 准备

### 原版游戏

Steam 安装 Snarl 1.0.3，记下目录，例如：

```
D:\Games\Snarl 1.0.3\
  Snarl.exe
  *.vox
  ...
```

### AGS 3.6.3.15 引擎

从 AGS 官方 release 下载 3.6.3.15 的 Windows 发布包：

https://github.com/adventuregamestudio/ags/releases/tag/v3.6.3.15

解压后需要里面的：

```
acwin.exe
SDL2.dll
```

> 版本必须严格是 **3.6.3.15**。补丁地址是按这个版本硬编码的，其它版本会报“引擎不匹配”。

### Python

Python 3.8+，无第三方依赖。

## 2. 合成

在本目录（`snarl/`）打开 PowerShell：

```powershell
python patch_snarl_engine.py `
  --game "D:\Games\Snarl 1.0.3" `
  --engine "D:\AGS\acwin.exe" `
  --out "D:\Games\Snarl 汉化版"
```

参数：

| 参数 | 说明 |
|---|---|
| `--game` | 原版游戏目录（必须含 `Snarl.exe`） |
| `--engine` | AGS 3.6.3.15 的 `acwin.exe` |
| `--out` | 输出目录，不存在会自动创建 |

脚本会：

1. 校验引擎字节（版本不对直接报错退出）
2. 打三处兼容补丁：
   - 角色 loop 越界检查
   - 阻塞式动画等待
   - 15 处淡出标志写入（NOP）
3. 写入新引擎 + 原版数据
4. 复制 `Snarl.tra`、`zh.ttf`、`acsetup.cfg`
5. 复制原版运行库（`SDL2.dll`、`*.vox` 等）

## 3. 产物

```
Snarl 汉化版\
  Snarl.exe        ← 3.6.3.15 引擎 + 原版数据 + 兼容补丁
  Snarl.tra        ← 中文翻译（含字体替换指令）
  zh.ttf           ← 中文像素字体
  acsetup.cfg      ← translation=Snarl
  SDL2.dll
  *.vox
```

## 4. 运行与验证

双击 `Snarl.exe`，然后按 [VERIFY.md](VERIFY.md) 检查，或运行：

```powershell
powershell -ExecutionPolicy Bypass -File verify_setup.ps1 -GameDir "D:\Games\Snarl 汉化版"
```

必须确认：

- 开场不黑屏
- 不报 `invalid loop`
- 对话不卡在动画等待
- 存档、读档、切场景正常

## 5. 常见错误

| 报错 | 原因 | 处理 |
|---|---|---|
| `引擎不匹配：... 期望 ... 实际 ...` | `acwin.exe` 不是 3.6.3.15 | 换官方 3.6.3.15 的 `acwin.exe` |
| 启动黑屏 | 没跑补丁脚本，或用了别的工具换引擎 | 必须用本脚本合成 |
| 对话卡住 | 同上，动画等待补丁没打上 | 同上 |
| 报 `invalid loop` | loop 越界补丁没打上 | 同上 |
| 中文变方块 | 缺 `zh.ttf` 或 `acsetup.cfg` 不对 | 检查 `translation=Snarl` |

## 6. 重新生成

改完译文后：

```powershell
python patch_snarl_engine.py --game ... --engine ... --out ...
```

输出目录会被覆盖，重新生成即可。

## 7. 回滚

直接删掉输出目录，或用 Steam「验证游戏文件完整性」恢复原版。
