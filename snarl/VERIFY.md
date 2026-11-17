# 安装后验证清单（Snarl）

## 1. 文件

- [ ] 游戏目录里有合成后的 `Snarl.exe`（3.6.3 引擎 + 原版数据）
- [ ] `Snarl.tra` 存在（约 140 KB）
- [ ] `zh.ttf` 存在
- [ ] `acsetup.cfg` 里是 `translation=Snarl`
- [ ] `logs\ags.log` 里有 `Translation loaded: Snarl.tra`

一键检查：

```powershell
powershell -ExecutionPolicy Bypass -File verify_setup.ps1 -GameDir "<汉化版目录>"
```

## 2. 关键兼容性（必须逐项确认）

Snarl 是 3.6.2 游戏跑在 3.6.3 引擎上，必须带三处补丁，否则会卡死：

- [ ] 进入游戏、走过开场对话，**不黑屏**
- [ ] 有角色出场的场景，**不报 `invalid loop`**
- [ ] 对话结束能继续，**不卡在动画等待**
- [ ] 存档、读档正常
- [ ] 切换场景正常

如果出现上面任一问题，说明 `Snarl.exe` 不是用 `patch_snarl_engine.py` 合成的，或 AGS 引擎版本不是 3.6.3.15。

## 3. 游戏内

- [ ] 主菜单中文
- [ ] 对话、选项中文
- [ ] 物品与界面中文
- [ ] 没有方块字、没有裁字

## 4. 回滚

直接用 Steam 重新校验游戏文件，或恢复原始 `Snarl.exe`。
