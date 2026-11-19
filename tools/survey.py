"""地形勘查：用 RCON 取樣地表高度與生態域，找適合放建築的平坦地點。

用法：python tools/survey.py <中心x> <中心z> [半徑=96] [間距=12]
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rcon  # noqa: E402

SNOWY = ["snowy_slopes", "grove", "frozen_peaks", "jagged_peaks", "snowy_plains", "snowy_taiga"]


def sample(cx, cz, radius, step):
    pts = {}
    area = f"{cx - radius - 16} {cz - radius - 16} {cx + radius + 16} {cz + radius + 16}"
    rcon.run([f"forceload add {area}", "kill @e[tag=ln_probe]",
              f"summon marker {cx} 100 {cz} {{Tags:[\"ln_probe\"]}}"])
    for x in range(cx - radius, cx + radius + 1, step):
        for z in range(cz - radius, cz + radius + 1, step):
            cmds = [f"spreadplayers {x} {z} 0 1 false @e[tag=ln_probe,limit=1]",
                    "data get entity @e[tag=ln_probe,limit=1] Pos[1]"]
            cmds += [f"execute at @e[tag=ln_probe,limit=1] if biome ~ ~ ~ minecraft:{b}" for b in SNOWY]
            res = rcon.run(cmds)
            m = re.search(r"([-\d.]+)d", res[1][1])
            if not m:
                continue
            y = float(m.group(1))
            biome = next((b for b, (_, out) in zip(SNOWY, res[2:]) if "passed" in out), "-")
            pts[(x, z)] = (y, biome)
    rcon.run(["kill @e[tag=ln_probe]", f"forceload remove {area}"])
    return pts


if __name__ == "__main__":
    cx, cz = int(sys.argv[1]), int(sys.argv[2])
    radius = int(sys.argv[3]) if len(sys.argv) > 3 else 96
    step = int(sys.argv[4]) if len(sys.argv) > 4 else 12
    pts = sample(cx, cz, radius, step)
    # 平坦度：與相鄰 8 點的最大高低差
    scored = []
    for (x, z), (y, b) in pts.items():
        nb = [pts[(x + dx, z + dz)][0] for dx in (-step, 0, step) for dz in (-step, 0, step)
              if (x + dx, z + dz) in pts]
        if len(nb) < 9 or b == "-":
            continue
        scored.append((max(nb) - min(nb), -y, x, z, y, b))
    scored.sort()
    print("最平坦的雪地候選點（高低差, x, z, 高度, 生態域）：")
    for spread, _, x, z, y, b in scored[:12]:
        print(f"  差 {spread:5.1f}  ({x}, {z})  y={y:.0f}  {b}")
    zs = sorted({z for _, z in pts})
    xs = sorted({x for x, _ in pts})
    print("\n高度圖（列=z，欄=x，* 表示非雪地）:")
    for z in zs:
        row = []
        for x in xs:
            y, b = pts.get((x, z), (0, "-"))
            row.append(f"{int(y):4d}{'*' if b == '-' else ' '}")
        print(f"{z:6d} " + "".join(row))
