#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kathy Rain 引擎合成脚本

用途：把自编译的 AGS 3.6.3.15 引擎与原版游戏数据拼成一个可运行的 exe。

关键点（40 号房间黑屏的根因）：
    原版 exe 的数据包以 16 字节的尾部标记结束：

        [引擎长度 4 字节][CLIB 4][01 02 03 04][SIGE 4]

    引擎长度必须写在“文件末尾 -16”处的 4 字节里。
    如果按常见做法写在“末尾 -20”处、且写 8 字节，会覆盖数据包
    尾部目录前的真实数据，导致最后一个房间（room40.crm）读取时
    "Unexpected end of file"，表现为黑屏/卡死。

用法：
    python pack_engine.py <原版exe> <自编译引擎exe> <输出exe>

示例：
    python pack_engine.py "KathyRain.exe.orig" "ags.exe" "KathyRain.exe"
"""

import struct
import sys
from pathlib import Path

# Kathy Rain 原版 exe 中游戏数据的起始偏移
DATA_OFFSET = 2146816


def pack(original_exe: Path, engine_exe: Path, output_exe: Path) -> None:
    engine = engine_exe.read_bytes()
    original = original_exe.read_bytes()

    if len(original) <= DATA_OFFSET:
        raise SystemExit("原版 exe 太小，数据偏移不正确")
    if len(engine) > 0x7FFFFFFF:
        raise SystemExit("引擎过大")

    data = original[DATA_OFFSET:]

    with output_exe.open("wb") as f:
        f.write(engine)
        f.write(data)
        # 引擎长度写在文件末尾 -16 处的 4 字节
        f.seek(-16, 2)
        f.write(struct.pack("<I", len(engine)))

    # 简单校验：尾部标记仍然存在
    out = output_exe.read_bytes()
    if out[-4:] != b"SIGE":
        raise SystemExit("尾部标记 SIGE 丢失，打包方式错误")
    stored = struct.unpack("<I", out[-16:-12])[0]
    if stored != len(engine):
        raise SystemExit("引擎长度写入位置错误")

    print(f"OK: {output_exe} ({len(out)} bytes)")
    print(f"    引擎长度 = {len(engine)} (0x{len(engine):X})")
    print(f"    数据长度 = {len(data)}")


def main() -> None:
    if len(sys.argv) != 4:
        print(__doc__)
        raise SystemExit(1)
    pack(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))


if __name__ == "__main__":
    main()
