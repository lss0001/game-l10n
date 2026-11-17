# 安装后验证清单（Lamplight City）

## 1. 文件

- [ ] 游戏目录里有补丁版 `German.tra`（约 1.33 MB，不是原版 1.45 MB）
- [ ] `agsfnt0.ttf` ~ `agsfnt7.ttf` 共 8 个都在
- [ ] `acsetup.cfg` 里是 `translation=Deutsch`
- [ ] 启动一次后，`logs\ags.log` 里有 `Translation loaded: German.tra`

一键检查：

```powershell
powershell -ExecutionPolicy Bypass -File verify_setup.ps1 -GameDir "<游戏目录>"
```

## 2. 游戏内

- [ ] Settings → Language 显示 Deutsch，且已重启
- [ ] 主菜单是中文
- [ ] 对话、旁白是中文
- [ ] 对话选项是中文
- [ ] 物品描述、案件档案是中文
- [ ] 没有方块字、没有文字被裁掉

## 3. 故意保留英文的地方（不是 bug）

- [ ] 图片里的文字（报纸、信件、招牌）保持英文——属于美术资源
- [ ] 设置菜单中部分文字来自图片资源

## 4. 回滚

- [ ] 把 `German.tra.orig` 改回 `German.tra`
- [ ] 删除 `agsfnt0.ttf` ~ `agsfnt7.ttf`
- [ ] 游戏里把语言切回 English
