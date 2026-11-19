"""從世界存檔（region 檔）讀出地表高度圖，給建築生成器用（不需要開伺服器）。

用法：python tools/heightmap.py <世界資料夾> <x1> <z1> <x2> <z2> <輸出.json>
輸出 JSON：{"x1","z1","x2","z2","top":[[...]]}，top[z-z1][x-x1] = 最上層實心方塊的 y
（使用 WORLD_SURFACE：雪層、粉雪都算地表）
"""
import gzip
import json
import struct
import sys
import zlib
from pathlib import Path

MIN_Y = -64


# ---------------------------------------------------------------- 最小 NBT 解析器
def read_nbt(buf):
    pos = 0

    def take(n):
        nonlocal pos
        b = buf[pos:pos + n]
        pos += n
        return b

    def payload(t):
        if t == 1:
            return struct.unpack(">b", take(1))[0]
        if t == 2:
            return struct.unpack(">h", take(2))[0]
        if t == 3:
            return struct.unpack(">i", take(4))[0]
        if t == 4:
            return struct.unpack(">q", take(8))[0]
        if t == 5:
            return struct.unpack(">f", take(4))[0]
        if t == 6:
            return struct.unpack(">d", take(8))[0]
        if t == 7:
            n = struct.unpack(">i", take(4))[0]
            return take(n)
        if t == 8:
            n = struct.unpack(">H", take(2))[0]
            return take(n).decode("utf-8", "replace")
        if t == 9:
            et = take(1)[0]
            n = struct.unpack(">i", take(4))[0]
            return [payload(et) for _ in range(n)]
        if t == 10:
            d = {}
            while True:
                tt = take(1)[0]
                if tt == 0:
                    return d
                name = take(struct.unpack(">H", take(2))[0]).decode("utf-8", "replace")
                d[name] = payload(tt)
        if t == 11:
            n = struct.unpack(">i", take(4))[0]
            return list(struct.unpack(f">{n}i", take(4 * n)))
        if t == 12:
            n = struct.unpack(">i", take(4))[0]
            return list(struct.unpack(f">{n}q", take(8 * n)))
        raise ValueError(f"未知 NBT 型別 {t}")

    t = take(1)[0]
    take(struct.unpack(">H", take(2))[0])
    return payload(t)


def chunk_nbt(region_dir, cx, cz):
    rf = Path(region_dir) / f"r.{cx >> 5}.{cz >> 5}.mca"
    if not rf.exists():
        return None
    with open(rf, "rb") as f:
        idx = 4 * ((cx & 31) + (cz & 31) * 32)
        f.seek(idx)
        loc = struct.unpack(">I", f.read(4))[0]
        if loc == 0:
            return None
        f.seek((loc >> 8) * 4096)
        length, ctype = struct.unpack(">IB", f.read(5))
        data = f.read(length - 1)
    raw = zlib.decompress(data) if ctype == 2 else gzip.decompress(data) if ctype == 1 else data
    return read_nbt(raw)


def unpack_heightmap(longs, bits=9):
    per = 64 // bits
    mask = (1 << bits) - 1
    vals = []
    for v in longs:
        v &= (1 << 64) - 1
        for i in range(per):
            vals.append((v >> (i * bits)) & mask)
            if len(vals) == 256:
                return vals
    return vals


def heights(world, x1, z1, x2, z2, kind):
    region = Path(world) / "region"
    top = [[None] * (x2 - x1 + 1) for _ in range(z2 - z1 + 1)]
    for cx in range(x1 >> 4, (x2 >> 4) + 1):
        for cz in range(z1 >> 4, (z2 >> 4) + 1):
            nbt = chunk_nbt(region, cx, cz)
            if not nbt or "Heightmaps" not in nbt:
                continue
            vals = unpack_heightmap(nbt["Heightmaps"][kind])
            for i, h in enumerate(vals):
                x = cx * 16 + (i & 15)
                z = cz * 16 + (i >> 4)
                if x1 <= x <= x2 and z1 <= z <= z2:
                    top[z - z1][x - x1] = h + MIN_Y - 1
    return top


if __name__ == "__main__":
    world, *nums, out = sys.argv[1:]
    x1, z1, x2, z2 = map(int, nums)
    t = heights(world, x1, z1, x2, z2, "WORLD_SURFACE")          # 含雪層、粉雪
    s = heights(world, x1, z1, x2, z2, "MOTION_BLOCKING_NO_LEAVES")  # 踩得住的實心地面
    missing = sum(v is None for row in t for v in row)
    Path(out).write_text(json.dumps({"x1": x1, "z1": z1, "x2": x2, "z2": z2, "top": t, "solid": s}), encoding="utf-8")
    print(f"已輸出 {out}：{x2 - x1 + 1}×{z2 - z1 + 1}，缺少 {missing} 格")
