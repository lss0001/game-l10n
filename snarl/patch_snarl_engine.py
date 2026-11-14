#!/usr/bin/env python3
"""把 Snarl 1.0.3 原版 exe 与 AGS 3.6.3.15 引擎合成为汉化版 exe。

用法：
    python patch_snarl_engine.py --game "C:\\Games\\Snarl 1.0.3" ^
        --engine "C:\\AGS\\acwin.exe" --out "C:\\Games\\Snarl 汉化版"

说明：
- --game   原版游戏目录（含 Snarl.exe）
- --engine AGS 3.6.3.15 的 acwin.exe（官方发布包里的 Windows 引擎）
- --out    输出目录，会生成 Snarl.exe 并复制汉化文件

合成后会应用三处兼容性修复（否则 3.6.3 引擎跑这个 3.6.2 游戏会卡死）：
1. 角色 loop 越界检查（否则报 invalid loop 崩溃）
2. 阻塞式动画等待（否则对话卡住不动）
3. 淡出标志写入（否则黑屏、进不了剧情）
"""

import argparse
import os
import shutil
import struct
import sys

# VA -> 文件偏移（PE 映像基址 0x401000，文件对齐 0x400）
def va_to_off(va):
    return 0x400 + (va - 0x401000)

# (地址, 原始字节, 补丁字节, 说明)
PATCHES = [
    (0x418999, b"\x75\x4B", b"\xEB\x4B", "角色 loop 越界检查"),
    (0x409806, b"\x74\x14", b"\xEB\x14", "跳过阻塞式动画等待"),
]

# 淡出标志写入点，全部 NOP 掉（地址, 长度）
NOP_SITES = [
    (0x422A37, 5), (0x44C7FD, 5), (0x478DCE, 10), (0x484A44, 10),
    (0x484A94, 6), (0x484ABC, 5), (0x4856F3, 5), (0x4C3654, 6),
    (0x4C36C0, 7), (0x4C3720, 7), (0x4C385C, 6), (0x4C3886, 6),
    (0x4C3A1A, 6), (0x4C3A33, 6), (0x52B9AB, 5),
]


def image_end(path):
    with open(path, "rb") as f:
        head = f.read(4096)
    e_lfanew = struct.unpack("<I", head[0x3C:0x40])[0]
    num = struct.unpack("<H", head[e_lfanew + 6:e_lfanew + 8])[0]
    opt = struct.unpack("<H", head[e_lfanew + 20:e_lfanew + 22])[0]
    off = e_lfanew + 24 + opt
    end = 0
    for i in range(num):
        base = off + 40 * i
        vsz, va, rsz, ro = struct.unpack("<IIII", head[base + 8:base + 24])
        end = max(end, ro + rsz)
    return end


def apply_patches(engine):
    engine = bytearray(engine)
    for va, old, new, desc in PATCHES:
        o = va_to_off(va)
        cur = bytes(engine[o:o + len(old)])
        if cur != old:
            sys.exit(
                "引擎不匹配：%s 处期望 %s，实际 %s。\n"
                "请确认使用的是 AGS 3.6.3.15 的 acwin.exe。"
                % (desc, old.hex(), cur.hex())
            )
        engine[o:o + len(new)] = new
    for va, n in NOP_SITES:
        o = va_to_off(va)
        engine[o:o + n] = b"\x90" * n
    print("已应用兼容性修复：loop 检查、动画等待、淡出黑屏")
    return bytes(engine)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True, help="原版游戏目录")
    ap.add_argument("--engine", required=True, help="AGS 3.6.3.15 acwin.exe 路径")
    ap.add_argument("--out", required=True, help="输出目录")
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    src_exe = os.path.join(args.game, "Snarl.exe")
    if not os.path.isfile(src_exe):
        sys.exit("找不到原版 Snarl.exe：%s" % src_exe)
    if not os.path.isfile(args.engine):
        sys.exit("找不到引擎 acwin.exe：%s" % args.engine)

    os.makedirs(args.out, exist_ok=True)
    dst_exe = os.path.join(args.out, "Snarl.exe")

    data_off = image_end(src_exe)
    engine = apply_patches(open(args.engine, "rb").read())

    with open(src_exe, "rb") as fi, open(dst_exe, "wb") as fo:
        fo.write(engine)
        fi.seek(data_off)
        while True:
            chunk = fi.read(8 * 1024 * 1024)
            if not chunk:
                break
            fo.write(chunk)
        fo.seek(-20, 2)
        fo.write(struct.pack("<q", len(engine)))

    print("已生成：%s" % dst_exe)

    shutil.copy(os.path.join(here, "Snarl.tra"), args.out)
    shutil.copy(os.path.join(here, "acsetup.cfg"), args.out)
    shutil.copy(os.path.join(here, "fonts", "zh.ttf"),
                os.path.join(args.out, "zh.ttf"))

    for name in ("SDL2.dll", "audio.vox", "winsetup.exe"):
        src = os.path.join(args.game, name)
        if os.path.isfile(src):
            shutil.copy(src, args.out)

    print("已复制：Snarl.tra / zh.ttf / acsetup.cfg / SDL2.dll / audio.vox")
    print("完成。双击输出目录里的 Snarl.exe 即可运行。")


if __name__ == "__main__":
    main()
