import json, os, re, struct, sys

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = json.load(open(os.path.join(BASE, "source.json"), encoding="utf-8"))
TR = json.load(open(os.path.join(BASE, "translated.json"), encoding="utf-8")) if os.path.exists(os.path.join(BASE, "translated.json")) else {}
MANUAL = json.load(open(os.path.join(BASE, "manual.json"), encoding="utf-8")) if os.path.exists(os.path.join(BASE, "manual.json")) else {}
TR.update(MANUAL)

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, "Deutsch.tra")
FONT_SIZE = int(sys.argv[2]) if len(sys.argv) > 2 else 12
GAME_UID = 5934168
GAME_NAME = "Kathy Rain"

PWD = b"Avis Durgan"


def enc(bs):
    o = bytearray()
    for i, b in enumerate(bs):
        o.append((b + PWD[i % 11]) & 0xFF)
        if b == 0:
            break
    return bytes(o)


def es(bs, o):
    o += struct.pack("<i", len(bs) + 1)
    o += enc(bs + b"\0")


def ps(bs, o):
    o += struct.pack("<i", len(bs))
    o += bs


def block(o, i, c):
    o += struct.pack("<i", i)
    o += struct.pack("<i", len(c))
    o += c


def ext(o, n, c):
    o += struct.pack("<i", 0)
    o += n.encode().ljust(16, b"\0")
    o += struct.pack("<q", len(c))
    o += c


def normalize(key, val):
    key = key.rstrip("\x00")
    val = val.replace("\x00", "").strip()
    # 去掉译文开头所有伪造的 &数字 标记
    val = re.sub(r"^(?:&\d+\s*)+", "", val).strip().rstrip("&").strip()
    m = re.match(r"^&(\d+)\s*", key)
    if m:
        val = "&" + m.group(1) + " " + val
    return key, val


def main():
    import os as _os
    _ids = _os.environ.get("KR_FONT_IDS", "").strip()
    _list = [int(x) for x in _ids.split(",") if x.strip()] if _ids else list(range(20))
    fonts = bytearray()
    fonts += struct.pack("<i", len(_list))
    fonts += struct.pack("<i", 3060300)
    for fid in _list:
        fonts += struct.pack("<15i", fid, -1, 0, 0, 4, FONT_SIZE, -1, 0, 0, 0, 0, 0, 0, 0, 0)
        fonts += struct.pack("<i", 6) + b"zh.ttf"
    if FONT_SIZE <= 0:
        fonts = None

    out = bytearray(b"AGSTranslation\0")
    c = bytearray()
    c += struct.pack("<i", GAME_UID)
    es(GAME_NAME.encode(), c)
    block(out, 2, bytes(c))

    c = bytearray()
    n = 0
    for x in SRC:
        zh = TR.get(str(x["id"]))
        if not zh:
            continue
        key, val = normalize(x["en"], zh)
        if not key or not val:
            continue
        es(key.encode("utf-8"), c)
        es(val.encode("utf-8"), c)
        n += 1

    # 额外键（游戏里存在但不在 source.json 的字符串，如语言名 "Deutsch"）
    extra_path = os.path.join(BASE, "extra_keys.json")
    if os.path.exists(extra_path):
        extra = json.load(open(extra_path, encoding="utf-8"))
        for k, v in extra.items():
            k = k.strip()
            v = v.strip()
            if k and v:
                es(k.encode("utf-8"), c)
                es(v.encode("utf-8"), c)
                n += 1

    es(b"", c)
    es(b"", c)
    block(out, 1, bytes(c))

    c = bytearray()
    c += struct.pack("<iiii", -1, -1, -1, 0)
    block(out, 3, bytes(c))

    c = bytearray()
    c += struct.pack("<i", 1)
    ps(b"encoding", c)
    ps(b"utf-8", c)
    ext(out, "ext_sopts", bytes(c))
    if fonts is not None:
        ext(out, "ext_fonts", bytes(fonts))

    out += struct.pack("<i", -1)
    open(OUT, "wb").write(out)
    print("entries", n, "bytes", len(out), "->", OUT)


if __name__ == "__main__":
    main()
