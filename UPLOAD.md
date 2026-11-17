# 上传工单：把汉化补丁上传到 GitHub

本工单用于把一款游戏的汉化补丁整理并上传到 `game-l10n` 仓库。按顺序执行即可。

## 0. 前置条件

- 已安装 Git
- 已登录 GitHub（二选一）：
  - `gh auth login`（推荐）
  - 或配置好 Personal Access Token（HTTPS 推送时当密码用）

## 1. 克隆仓库

```powershell
git clone https://github.com/lss0001/game-l10n.git
cd game-l10n
git pull
```

## 2. 新建游戏文件夹

命名规则：小写英文 / 拼音，用 `-` 连接，例如：

```
kathy-rain/
lamplight-city/
snarl/
```

## 3. 放入文件

最低要求：

```
<游戏名>/
  README.md            安装说明（见下方模板）
  LICENSE.md           许可说明
  <翻译文件>.tra        翻译文件
  fonts/
    zh.ttf             中文字体（如需要）
    LICENSE-OFL.txt    字体许可
```

可选：

```
  source/              翻译工程（原文对照、人工校对、生成脚本）
  *.py                 引擎合成 / 打包脚本
```

**绝对不要放**：

- 游戏本体 exe、数据文件、素材、音频
- 任何破解/绕过 DRM 的内容

## 4. 更新根目录 README

在「已收录」表格加一行：

```markdown
| [游戏名](游戏名/) | 引擎说明 | 词条数，字体/脚本说明 |
```

并更新目录结构树。

## 5. 检查

```powershell
git status
git diff --stat
```

确认：

- 只新增了该游戏文件夹与根 README
- 没有超过 100 MB 的单个文件（GitHub 限制）
- `.tra`、`zh.ttf` 存在且能打开

## 6. 提交

提交信息要求：**简洁、直接描述改动，不要加“游戏名：”前缀**。

推荐写法：

```
汉化文件、字体与安装说明
补充安装说明
修正译文与字体许可
```

不要写：

```
Kathy Rain：汉化文件...
```

命令：

```powershell
git add <游戏名> README.md
git commit -m "汉化文件、字体与安装说明"
```

## 7. 推送

```powershell
git push
```

首次推送若提示认证失败：

- 用 `gh auth login` 重新登录
- 或把 Token 当作 HTTPS 密码

## 8. 验证

打开仓库网页确认：

- 新文件夹存在
- README 能正常显示
- 根 README 表格已更新

## 9. 可选：发布 Release

如果补丁文件较大或需要打包下载：

1. 在仓库页面点「Releases」→「Draft a new release」
2. Tag 用游戏名，如 `kathy-rain-v1`
3. 上传 zip（**只含补丁文件，不含游戏本体**）
4. 写更新说明后发布

## README 模板

```markdown
# 游戏名 简体中文汉化

把《游戏名》的英文文本替换为简体中文的民间汉化补丁。

适用于 Steam 正版（AppID xxxxx）。包含 **N 条翻译** 和一个配套的中文像素字体。

> 本仓库不包含游戏本体。请先购买正版。

## 这个补丁包含什么

- `xxx.tra`：中文翻译文件
- `fonts/zh.ttf`：开源像素中文字体
- `source/`：翻译工程文件（可选）
- `engine-patches.md`：引擎补丁说明（如需要）

## 安装前需要知道的一件事

（例如：原版引擎不支持中文，需要自编译引擎 / 语言槽位限制等）

## 安装

1. 打开游戏目录
2. …
3. …

## 常见问题

**进游戏还是英文？**

- …

## 卸载

1. …
```

## 常见失败原因

| 现象 | 原因 | 处理 |
|---|---|---|
| 推送 403 | 未登录 / Token 无 repo 权限 | `gh auth login` 或换 Token |
| 文件过大 | 超过 100 MB | 拆分或使用 Release 附件 |
| 网页乱码 | 文件不是 UTF-8 | 用 UTF-8 无 BOM 重新保存 |
| 补丁无效 | 语言槽 / 文件名不对 | 检查 `acsetup.cfg` 与 `.tra` 文件名 |
