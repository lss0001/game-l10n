#!/usr/bin/env python3
"""把 Snarl 1.0.3 原版 exe 与 AGS 3.6.3 引擎合成为汉化版 exe。

用法：
    python patch_snarl_engine.py --game "C:\\Games\\Snarl 1.0.3" ^
        --engine "C:\\AGS\\acwin.exe" --out "C:\\Games\\Snarl 汉化版"

说明：
- --game   原版游戏目录（含 Snarl.exe）
- --engine AGS 3.6.3 的 acwin.exe（官方发布包里的 Windows 引擎）
- --out    输出目录，会生成 Snarl.exe 并复制汉化文件

原理：
    AGS 游戏 exe = 引擎 PE + 附加的游戏数据包（CLIB）。
    用 3.6.3 引擎替换原 3.6.2 引擎，保留原游戏数据，并修正文件尾部
    记录的数据偏移，即可支持 Unicode 与字体替换。
"""

import argparse
import os
import shutil
import struct
import sys


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True, help="原版游戏目录")
    ap.add_argument("--engine", required=True, help="AGS 3.6.3 acwin.exe 路径")
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
    engine = open(args.engine, "rb").read()

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

    # 复制汉化资源
    shutil.copy(os.path.join(here, "Snarl.tra"), args.out)
    shutil.copy(os.path.join(here, "acsetup.cfg"), args.out)
    os.makedirs(os.path.join(args.out, "fonts"), exist_ok=True)
    shutil.copy(os.path.join(here, "fonts", "zh.ttf"),
                os.path.join(args.out, "zh.ttf"))

    # 原版运行库/音频
    for name in ("SDL2.dll", "audio.vox", "winsetup.exe"):
        src = os.path.join(args.game, name)
        if os.path.isfile(src):
            shutil.copy(src, args.out)

    print("已复制：Snarl.tra / zh.ttf / acsetup.cfg / SDL2.dll / audio.vox")
    print("完成。双击输出目录里的 Snarl.exe 即可运行。")


if __name__ == "__main__":
    main()
