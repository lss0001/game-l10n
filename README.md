# 游戏汉化补丁合集

个人制作/整理的游戏中文本地化补丁仓库，**一个游戏一个文件夹**。

> 本仓库**不包含任何游戏本体**，只包含翻译文本、开源字体与合成脚本。请先购买正版游戏。

## 已收录

| 游戏 | 引擎 | 说明 |
|---|---|---|
| [Lamplight City](lamplight-city/) | AGS 3.6 | 完整汉化，10,720 条词条，含像素字体 |
| [Snarl](snarl/) | AGS 3.6.2 → 3.6.3 | 1,641 条词条，附带引擎合成脚本 |
| [Kathy Rain](kathy-rain/) | AGS 3.3 → 3.6.3.15 | 4,688 条词条，含像素字体与引擎补丁说明 |

## 目录结构

```
/
├── README.md                 ← 本文件
├── lamplight-city/           《Lamplight City》简体中文汉化
│   ├── German.tra            ← 翻译文件
│   ├── fonts/zh.ttf          ← 开源中文字体
│   ├── README.md             ← 安装说明
│   └── LICENSE.md
├── snarl/                    《Snarl》简体中文汉化
│   ├── Snarl.tra             ← 翻译文件
│   ├── fonts/zh.ttf          ← 开源中文字体
│   ├── patch_snarl_engine.py ← 引擎合成脚本（需自备原版与 AGS 3.6.3）
│   ├── README.md
│   └── LICENSE.md
├── kathy-rain/                《Kathy Rain》简体中文汉化
│   ├── 简体中文.tra           ← 翻译文件
│   ├── fonts/zh.ttf           ← 开源中文字体（Zpix）
│   ├── engine-patches.md      ← 引擎补丁与打包说明
│   ├── source/                ← 翻译工程文件
│   ├── README.md
│   └── LICENSE.md
└── （以后新增的游戏，同样是一个文件夹）
```

## 新增游戏约定

1. 在仓库根目录新建 `<游戏名>/` 文件夹
2. 放入翻译文件、字体（如需要）、`README.md`、`LICENSE.md`
3. 在本文件「已收录」表格里加一行

## 许可

- 各游戏译文许可见对应文件夹的 `LICENSE.md`
- 字体许可见各游戏 `fonts/LICENSE-OFL.txt`
- 游戏版权归各自作者/发行商所有
