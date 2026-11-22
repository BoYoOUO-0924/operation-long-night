"""第一章：黑石海岸砲台 生成器（天然海崖改造）。

地點：第五章雪山東側的天然石岸（x -16..140, z 1250..1480）。海在東邊，海岸線大致南北走向。
  北段：高台地 y≈119～128，東側是 60 格高的垂直海崖  → 主陣地（雷達 A 北崖、雷達 B 中央、觀測站）
  中段：海岸岩棚 y≈85～95，面海的崖高約 20 格        → 沙灘、崖壁小路、探照燈塔、防空砲、大門
  南段：岬角 y≈100～110                              → 燈塔（雷達 C）
  西側：雪山（snowy_slopes）                         → 「藏著巨砲的山體」

風格：二戰舊砲台改建——混凝土砲堡、戰壕、沙包，加裝現代雷達、貨櫃、偽裝網。

輸出：
  functions/build/coast_terrain.mcfunction  地形改造（只跑一次：去樹、去雪、地表換成黑石海岸、挖沙灘、崖壁小路、生物群系改成會下雨）
  functions/build/coast_battery.mcfunction  建築（每次開關卡都重建，雷達會被炸掉）
  generators/out/blackstone_coast.json      錨點
執行前先產生高度圖：
  python tools/heightmap.py server/longnight -48 1248 207 1503 generators/out/heightmap_ch01.json
座標全部是絕對座標（輸出時用 execute positioned 0 0 0 執行）。
"""
import json
import math
import random
from pathlib import Path

from canvas import Canvas

ROOT = Path(__file__).resolve().parent.parent
HM = json.loads((ROOT / "generators/out/heightmap_ch01.json").read_text(encoding="utf-8"))
SEA = 62                                   # 海面高度（水的最上層方塊）
BOX = (-16, 1250, 140, 1480)               # 改造範圍 x1 z1 x2 z2
rng = random.Random(11)


def solid(x, z):
    return HM["solid"][z - HM["z1"]][x - HM["x1"]]


def is_sea(x, z):
    return solid(x, z) <= SEA


def sea_dist(x, z, r=12):
    """到最近海面的水平距離（r 以內，找不到回傳 r+1）"""
    best = r + 1
    for dx in range(-r, r + 1, 2):
        for dz in range(-r, r + 1, 2):
            px, pz = x + dx, z + dz
            if HM["x1"] <= px <= HM["x2"] and HM["z1"] <= pz <= HM["z2"] and is_sea(px, pz):
                best = min(best, math.hypot(dx, dz))
    return best


def chunks(x1, y1, z1, x2, y2, z2, step=32):
    """把大範圍切成每塊 ≤ 32768 格（fill／fillbiome 的上限）"""
    hy = max(1, 32768 // (step * step))
    for x in range(x1, x2 + 1, step):
        for z in range(z1, z2 + 1, step):
            for y in range(y1, y2 + 1, hy):
                yield x, y, z, min(x + step - 1, x2), min(y + hy - 1, y2), min(z + step - 1, z2)


# ================================================================ 1. 地形改造（只跑一次）
T = []
X1, Z1, X2, Z2 = BOX
# 1a. 去掉雪、草、樹（整個範圍、地表附近 y 70～170）
for (a, b, cz, d, e, f) in chunks(X1, 70, Z1, X2, 170, Z2):
    for blk in ("snow", "grass", "tall_grass", "fern", "large_fern", "spruce_leaves", "oak_leaves", "birch_leaves",
                "spruce_log", "oak_log", "birch_log", "sweet_berry_bush", "dandelion", "poppy", "azure_bluet", "cornflower",
                "oxeye_daisy", "lily_of_the_valley", "allium", "red_tulip", "orange_tulip", "white_tulip", "pink_tulip"):
        T.append(f"fill {a} {b} {cz} {d} {e} {f} air replace {blk}")
# 1b. （第 1 版的 4×4 色塊已作廢：會變成棋盤格和直條紋。改成下面 1f 的逐格雜訊上色）

# 1c. 生物群系改成海灘（溫暖、晚上會下雨不會下雪）；西邊雪山不動
for (a, b, cz, d, e, f) in chunks(X1, 40, Z1, X2, 200, Z2, step=16):
    T.append(f"fillbiome {a} {b} {cz} {d} {e} {f} minecraft:beach replace minecraft:stony_shore")
    for bio in ("plains", "meadow", "taiga", "forest", "windswept_hills", "windswept_forest", "grove", "cold_ocean", "ocean",
                "deep_cold_ocean", "stony_peaks", "windswept_gravelly_hills", "old_growth_spruce_taiga", "snowy_taiga", "snowy_plains"):
        T.append(f"fillbiome {a} {b} {cz} {d} {e} {f} minecraft:beach replace minecraft:{bio}")

c = Canvas(seed=11)          # 地形裡要逐格放的部分（沙灘、小路）也用畫布


def _h(ix, iz, seed):
    n = (ix * 374761393 + iz * 668265263 + seed * 2246822519) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65535.0


def noise(x, z, scale, seed=0):
    """平滑的值雜訊 0..1（取代第 1 版的方塊亂數，才不會出現格子感）"""
    fx, fz = x / scale, z / scale
    ix, iz = math.floor(fx), math.floor(fz)
    tx, tz = fx - ix, fz - iz
    tx, tz = tx * tx * (3 - 2 * tx), tz * tz * (3 - 2 * tz)
    a = _h(ix, iz, seed) + (_h(ix + 1, iz, seed) - _h(ix, iz, seed)) * tx
    b = _h(ix, iz + 1, seed) + (_h(ix + 1, iz + 1, seed) - _h(ix, iz + 1, seed)) * tx
    return a + (b - a) * tz


def fbm(x, z, scale, seed=0):
    return 0.6 * noise(x, z, scale, seed) + 0.3 * noise(x, z, scale / 2.3, seed + 7) + 0.1 * noise(x, z, scale / 5, seed + 13)


# 海崖岩層：橫向分層（略微起伏），越低越黑；每層再用細雜訊混 3～4 種相近方塊
STRATA_LOW = [["basalt[axis=y]", "basalt[axis=y]", "smooth_basalt", "blackstone"],
              ["deepslate", "cobbled_deepslate", "tuff", "deepslate"],
              ["blackstone", "basalt[axis=y]", "polished_basalt[axis=y]", "blackstone"],
              ["tuff", "deepslate", "tuff", "andesite"]]
STRATA_HIGH = [["stone", "andesite", "tuff", "stone"],
               ["tuff", "basalt[axis=y]", "deepslate", "tuff"],
               ["andesite", "stone", "cobblestone", "andesite"],
               ["deepslate", "tuff", "basalt[axis=y]", "smooth_basalt"]]


def rock(x, y, z):
    wav = y + 3 * noise(x, z, 9, 3)
    band = int(wav // 4)
    pal = STRATA_LOW if y < 92 else STRATA_HIGH
    row = pal[band % len(pal)]
    k = int(noise(x * 1.7 + y * 3.1, z * 1.7 - y * 2.3, 2.2, 5) * len(row) * 0.999)
    return row[k]


def ground_top(x, z, y, steep, near):
    n = fbm(x, z, 14, 1)
    if near or y < 90:                              # 海岸岩棚：碎石、凝灰岩、黑石
        return "gravel" if n < 0.38 else ("tuff" if n < 0.55 else ("blackstone" if n < 0.7 else ("coarse_dirt" if n < 0.82 else "basalt[axis=y]")))
    if steep:                                        # 陡坡：露出岩石
        return rock(x, y, z)
    if n < 0.48:
        return "grass_block"
    if n < 0.6:
        return "coarse_dirt"
    if n < 0.68:
        return "rooted_dirt"
    if n < 0.76:
        return "gravel"
    return "grass_block" if noise(x, z, 3, 9) < 0.5 else "moss_block"


for x in range(X1, X2 + 1):
    for z in range(Z1, Z2 + 1):
        y = solid(x, z)
        if y <= SEA:
            continue
        nb = [solid(x + dx, z + dz) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))
              if HM["x1"] <= x + dx <= HM["x2"] and HM["z1"] <= z + dz <= HM["z2"]]
        low = min(nb) if nb else y
        steep = y - low >= 3
        near = sea_dist(x, z, 6) <= 5
        c.blocks[(x, y, z)] = ground_top(x, z, y, steep, near)
        sub = "dirt" if c.blocks[(x, y, z)] in ("grass_block", "coarse_dirt", "rooted_dirt", "moss_block") else None
        for yy in range(max(low + 1, SEA - 3), y):     # 露出來的側面（崖壁、台階）
            c.blocks[(x, yy, z)] = sub if (sub and y - yy <= 1 and not steep) else rock(x, yy, z)
# 1d. 沙灘：中段崖下（z 1392～1448），從崖腳往海延伸 14 格，由 y63 斜到水下
BEACH_Z = (1392, 1448)
beach_cells = []
for z in range(BEACH_Z[0], BEACH_Z[1] + 1):
    edge = next((x for x in range(40, 140) if is_sea(x, z)), None)     # 這一列海開始的 x
    if edge is None:
        continue
    width = 18 + round(4 * math.sin(z / 7.0)) + rng.choice([0, 0, 1])
    # 兩端收窄成小海灣
    t = (z - BEACH_Z[0]) / (BEACH_Z[1] - BEACH_Z[0])
    width = round(width * min(1, 4 * t, 4 * (1 - t)))
    for i in range(width):
        x = edge + i
        top = SEA + 2 if i < width * 0.25 else (SEA + 1 if i < width * 0.6 else (SEA if i < width * 0.8 else SEA - 1))
        for y in range(SEA - 6, top + 1):
            c.blocks[(x, y, z)] = "sand" if i > 2 else "gravel"
        if top <= SEA:
            pass
        else:
            for y in range(top + 1, top + 4):
                c.blocks[(x, y, z)] = "air"
        beach_cells.append((x, z))
        if i < 2 and c.chance(0.25):
            c.blocks[(x, top + 1, z)] = rng.choice(["cobblestone", "mossy_cobblestone", "andesite", "tuff"])
# 漂流木、廢鐵、翻覆的登陸艇殘骸（掩體）
for (x, z) in rng.sample(beach_cells, 10):
    c.blocks[(x, SEA + 2, z)] = rng.choice(["stripped_dark_oak_log[axis=x]", "stripped_spruce_log[axis=z]", "iron_bars", "anvil[facing=north]"])

# 1e. 崖壁小路：沙灘北段 → 之字形爬上岩棚（每 2 格升 1 格，3 格寬）
def path_leg(p0, p1, y0, y1):
    n = max(abs(p1[0] - p0[0]), abs(p1[1] - p0[1]))
    for k in range(n + 1):
        f = k / n
        x = round(p0[0] + (p1[0] - p0[0]) * f)
        z = round(p0[1] + (p1[1] - p0[1]) * f)
        y = round(y0 + (y1 - y0) * f)
        for w in (-1, 0, 1):
            px, pz = (x + w, z) if p0[0] == p1[0] else (x, z + w)
            for yy in range(SEA - 2, y):
                c.blocks.setdefault((px, yy, pz), "stone")
            c.blocks[(px, y, pz)] = "gravel" if c.chance(0.5) else "cobblestone"
            for yy in range(y + 1, max(y + 5, solid(px, pz) + 2)):     # 切成露天的凹槽，不要變隧道
                c.blocks[(px, yy, pz)] = "air"
        # 靠海那一側的木樁＋繩子欄杆
        if k % 3 == 0:
            ox, oz = (x + 2, z) if p0[0] == p1[0] else (x, z - 2)
            c.blocks[(ox, y + 1, oz)] = "spruce_fence"
    return (x, y, z)


def cliff_edge_x(z):
    return next((x for x in range(40, 140) if is_sea(x, z)), 100)


PZ = 1400
px0 = cliff_edge_x(PZ) - 1
top1 = path_leg((px0, PZ), (px0, PZ + 22), SEA + 1, SEA + 12)          # 第一段：沿崖腳往南爬
top2 = path_leg((px0 - 4, PZ + 22), (px0 - 4, PZ), SEA + 12, SEA + 23)  # 第二段：折返往北爬上岩棚
c.box(px0 - 3, SEA + 12, PZ + 21, px0 + 1, SEA + 12, PZ + 24, "cobblestone")       # 折返平台
c.box(px0 - 3, SEA + 13, PZ + 21, px0 + 1, SEA + 16, PZ + 24, "air")
PATH_TOP = (px0 - 4, SEA + 23, PZ)
terrain_cmds = T + [cmd.replace("~", "") for cmd in c.commands()]

# ================================================================ 2. 建築（每次開關卡重建）
b = Canvas(seed=21)
conc = b.pick([("light_gray_concrete", 55), ("andesite", 15), ("gray_concrete", 15), ("cracked_stone_bricks", 10), ("tuff", 5)])
sandbag = b.pick([("mud_bricks", 70), ("packed_mud", 30)])
anchors = {"enemy_spawns": {}}


def g(x, z):
    return solid(x, z)


def pad(x1, z1, x2, z2, y, blk=None):
    """整地：地基墊到 y（含），上方清空 12 格"""
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            for yy in range(min(g(x, z), y) - 2, y + 1):
                b.blocks[(x, yy, z)] = blk() if callable(blk) else (blk or conc())
            for yy in range(y + 1, y + 13):
                b.blocks.setdefault((x, yy, z), "air")


def sandbags(cx, cz, r, y, gap=None):
    """一圈沙包矮牆（2 格高），gap = 缺口方向角度（度）"""
    for k in range(int(2 * math.pi * r * 1.5)):
        ang = k / (r * 1.5)
        if gap is not None and abs(((math.degrees(ang) - gap + 180) % 360) - 180) < 25:
            continue
        x, z = round(cx + r * math.cos(ang)), round(cz + r * math.sin(ang))
        b.blocks[(x, y + 1, z)] = sandbag()
        b.blocks[(x, y + 2, z)] = "mud_brick_slab" if b.chance(0.7) else sandbag()


def camo(x1, z1, x2, z2, y):
    """偽裝網：柵欄柱撐起來的綠褐色地毯"""
    for (x, z) in [(x1, z1), (x1, z2), (x2, z1), (x2, z2)]:
        for yy in range(g(x, z) + 1, y):
            b.blocks[(x, yy, z)] = "spruce_fence"
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            if b.chance(0.85):
                b.blocks[(x, y, z)] = b.rng.choice(["green_carpet", "green_carpet", "brown_carpet", "moss_carpet"])


def radar_mast(cx, cz, y, h, tag, face=1):
    """格子鐵塔（承重柱＋橫樑）＋方塊拋物面天線（凹面朝東邊的海），饋源用避雷針"""
    for yy in range(y + 1, y + h):
        for (dx, dz) in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            b.blocks[(cx + dx, yy, cz + dz)] = "polished_basalt[axis=y]" if yy % 3 == 0 else "iron_bars"
        if yy % 4 == 0:
            b.box(cx - 1, yy, cz - 1, cx + 1, yy, cz + 1, "iron_block")
        b.blocks[(cx, yy, cz)] = "chain[axis=y]"
    top = y + h
    b.box(cx - 1, top, cz - 1, cx + 1, top, cz + 1, "polished_deepslate")     # 轉台
    b.blocks[(cx, top + 1, cz)] = "lodestone"
    dc = top + 5                                                             # 天線中心高度
    for a in range(-4, 5):            # 天線寬（z 方向）
        for v in range(-3, 4):        # 天線高
            e = (a / 4.5) ** 2 + (v / 3.5) ** 2
            if e > 1:
                continue
            depth = round((a * a + v * v) / 9.0)                             # 越外圈越往前凸 → 凹面
            x = cx + face * depth
            b.blocks[(x, dc + v, cz + a)] = "smooth_quartz" if e <= 0.62 else ("quartz_bricks" if (a + v) % 2 else "white_concrete")
            if (x - face, dc + v, cz + a) not in b.blocks:
                b.blocks[(x - face, dc + v, cz + a)] = "iron_bars" if abs(a) % 2 else "air"
    b.box(cx, top + 2, cz, cx, dc - 4, cz, "polished_basalt[axis=y]")
    for k in range(1, 4):                                                    # 饋源支架
        b.blocks[(cx + face * (2 + k), dc, cz)] = "lightning_rod[facing=east]" if face > 0 else "lightning_rod[facing=west]"
    b.blocks[(cx + face * 6, dc, cz)] = "redstone_lamp[lit=true]"


def radome(cx, cz, y, r=4):
    """雷達罩：白色球頂（雷達 B 用，從空中一眼認得出來）"""
    for dx in range(-r, r + 1):
        for dz in range(-r, r + 1):
            for dy in range(0, r + 2):
                d = math.sqrt(dx * dx + dz * dz + (dy - 1) ** 2)
                if r - 0.6 <= d <= r + 0.4:
                    b.blocks[(cx + dx, y + dy, cz + dz)] = "white_concrete" if (dx * 3 + dz + dy) % 7 else "light_gray_concrete"
                elif d < r - 0.6:
                    b.blocks[(cx + dx, y + dy, cz + dz)] = "air"
    b.blocks[(cx, y + r + 2, cz)] = "lightning_rod"


# ================================================================ 模組化零件（kitbash）
def wall_mix():
    return b.rng.choices(["light_gray_concrete", "andesite", "tuff", "cracked_stone_bricks", "stone"], [45, 20, 15, 12, 8])[0]


def mg_nest(x, z, face="east"):
    """半圈沙包機槍巢（開口朝後）"""
    y = g(x, z)
    dx, dz = {"east": (1, 0), "west": (-1, 0), "south": (0, 1), "north": (0, -1)}[face]
    for k in range(-2, 3):
        px, pz = x + 2 * dx + k * dz, z + 2 * dz + k * dx
        py = g(px, pz)
        b.blocks[(px, py + 1, pz)] = sandbag()
        b.blocks[(px, py + 2, pz)] = "mud_brick_slab"
    for side in (-1, 1):
        px, pz = x + dx + side * dz * 2, z + dz + side * dx * 2
        b.blocks[(px, g(px, pz) + 1, pz)] = sandbag()
    b.blocks[(x + dx, y + 1, z + dz)] = "polished_blackstone_wall"
    b.blocks[(x + dx, y + 2, z + dz)] = f"iron_trapdoor[facing={face},half=bottom,open=false]"
    b.blocks[(x, y + 1, z)] = "green_terracotta"                                   # 彈藥箱


def generator_set(x, z):
    """軍用發電機組：機身、排氣管、油桶"""
    y = g(x, z)
    pad(x - 1, z - 1, x + 2, z + 1, y)
    b.box(x, y + 1, z, x + 1, y + 1, z, "iron_block")
    b.blocks[(x, y + 2, z)] = "smoker[facing=south,lit=true]"
    b.blocks[(x + 1, y + 2, z)] = "iron_trapdoor[half=bottom]"
    b.blocks[(x + 1, y + 3, z)] = "lightning_rod"
    b.blocks[(x + 2, y + 1, z)] = "barrel[facing=up]"
    b.blocks[(x - 1, y + 1, z)] = "red_concrete"
    b.blocks[(x - 1, y + 2, z)] = "heavy_weighted_pressure_plate"


def ammo_stack(x, z):
    y = g(x, z)
    for (dx, dz, h) in [(0, 0, 2), (1, 0, 1), (0, 1, 1)]:
        for k in range(1, h + 1):
            b.blocks[(x + dx, g(x + dx, z + dz) + k, z + dz)] = b.rng.choice(["green_terracotta", "barrel[facing=up]", "spruce_planks"])
    b.blocks[(x, y + 3, z)] = "spruce_trapdoor[half=bottom]"


def hedgehog(x, z):
    """反登陸拒馬"""
    y = max(g(x, z), SEA + 1)
    b.blocks[(x, y + 1, z)] = "chain[axis=x]"
    b.blocks[(x, y + 2, z)] = "chain[axis=z]"
    b.blocks[(x, y + 1, z + 1)] = "iron_bars"
    b.blocks[(x + 1, y + 1, z)] = "iron_bars"


def wire(x1, z1, x2, z2):
    """鐵絲網：一排鐵柵欄，偶爾夾蜘蛛網"""
    n = max(abs(x2 - x1), abs(z2 - z1))
    for k in range(n + 1):
        x = round(x1 + (x2 - x1) * k / n)
        z = round(z1 + (z2 - z1) * k / n)
        b.blocks[(x, g(x, z) + 1, z)] = "cobweb" if b.chance(0.15) else "iron_bars"


def light_pole(x, z, h=5):
    y = g(x, z)
    for yy in range(y + 1, y + h):
        b.blocks[(x, yy, z)] = "polished_blackstone_wall"
    b.blocks[(x, y + h, z)] = "polished_blackstone_slab"
    b.blocks[(x, y + h - 1, z + 1)] = "lantern[hanging=true]"
    b.blocks[(x, y + h, z + 1)] = "polished_blackstone_slab"


def c4_point(name, x, y, z):
    anchors[f"c4_{name}"] = [x, y, z]
    b.blocks[(x, y, z)] = "iron_block"
    b.blocks[(x, y + 1, z)] = "heavy_weighted_pressure_plate"


# ---- 2a. 探照燈塔（岩棚邊，面海）
sx, sz = PATH_TOP[0] - 6, PATH_TOP[2] + 6
sy = max(g(x, z) for x in range(sx - 2, sx + 3) for z in range(sz - 2, sz + 3))
pad(sx - 2, sz - 2, sx + 2, sz + 2, sy)
for yy in range(sy + 1, sy + 6):
    for (dx, dz) in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
        b.blocks[(sx + dx, yy, sz + dz)] = "iron_bars" if yy % 2 else "polished_basalt"
b.box(sx - 2, sy + 6, sz - 2, sx + 2, sy + 6, sz + 2, "iron_block")
b.box(sx - 1, sy + 7, sz - 1, sx + 1, sy + 7, sz + 1, "iron_trapdoor[half=bottom]")
b.blocks[(sx, sy + 7, sz)] = "polished_blackstone"
b.blocks[(sx, sy + 8, sz)] = "redstone_lamp[lit=true]"
b.blocks[(sx + 1, sy + 8, sz)] = "sea_lantern"                               # 燈面朝海（東）
b.box(sx - 1, sy + 1, sz, sx - 1, sy + 5, sz, "chain[axis=y]")
# 供電箱＋電纜（燈座西側地面，關卡用可射擊的實體標出）
b.blocks[(sx - 4, sy + 1, sz)] = "gray_concrete"
b.blocks[(sx - 4, sy + 2, sz)] = "lever[face=floor,facing=east]"
b.box(sx - 3, sy + 1, sz, sx - 3, sy + 1, sz, "lightning_rod[facing=east]")
anchors["searchlight"] = [sx + 1, sy + 8, sz]
anchors["searchlight_cable"] = [sx - 4, sy + 1, sz]

# ---- 2b. 防空砲陣地（岩棚南段）
ax, az = PATH_TOP[0] - 22, PATH_TOP[2] + 28
ay = round(sum(g(x, z) for x in range(ax - 5, ax + 6) for z in range(az - 5, az + 6)) / 121)
pad(ax - 5, az - 5, ax + 5, az + 5, ay)
sandbags(ax, az, 5, ay, gap=200)
b.box(ax - 1, ay + 1, az - 1, ax + 1, ay + 1, az + 1, "polished_deepslate")
b.blocks[(ax, ay + 2, az)] = "anvil[facing=east]"
b.blocks[(ax, ay + 3, az)] = "dark_gray_concrete" if False else "polished_blackstone_bricks"
for (dz, k) in ((-1, 0), (1, 0)):                                            # 雙聯裝砲管（斜指天空）
    for i in range(1, 5):
        b.blocks[(ax + i, ay + 3 + i, az + dz)] = "end_rod[facing=up]"
for (x, z) in [(ax - 3, az + 3), (ax - 3, az + 2), (ax - 2, az + 3)]:       # 油料桶（可打爆）
    b.blocks[(x, ay + 1, z)] = "red_concrete"
    b.blocks[(x, ay + 2, z)] = "iron_trapdoor[half=bottom]"
for (x, z) in [(ax + 3, az - 3), (ax + 3, az - 2)]:                          # 彈藥箱
    b.blocks[(x, ay + 1, z)] = "green_terracotta"
anchors["aa_gun"] = [ax, ay + 3, az]
anchors["aa_barrels"] = [ax - 3, ay + 1, az + 3]

# ---- 2c. 圍牆與主陣地大門（岩棚往北爬上台地的坡道口）
gx, gz = 44, 1372
gy = g(gx, gz)
for x in range(18, 58):                                                      # 東西向圍牆
    z = gz + (0 if abs(x - gx) <= 3 else round(2 * math.sin(x / 5.0)))
    base_y = g(x, z)
    if base_y <= SEA:
        continue
    if abs(x - gx) <= 3:
        continue
    for yy in range(base_y - 1, base_y + 4):
        b.blocks[(x, yy, z)] = conc()
    b.blocks[(x, base_y + 4, z)] = "iron_bars"                               # 鐵絲網
for yy in range(gy + 1, gy + 7):                                             # 門柱
    for xx in (gx - 4, gx + 4):
        b.blocks[(xx, yy, gz)] = "polished_blackstone_bricks"
b.box(gx - 4, gy + 6, gz, gx + 4, gy + 6, gz, "polished_blackstone_bricks")
b.box(gx - 3, gy, gz - 2, gx + 3, gy, gz + 2, "gravel")
GATE = (gx - 3, gy + 1, gz, gx + 3, gy + 5, gz)
b.box(*GATE, "iron_block")                                                   # 大門（開門時清成空氣）
b.blocks[(gx + 5, gy + 2, gz + 1)] = "polished_blackstone_button[face=wall,facing=south]"
anchors["gate"] = list(GATE)
anchors["gate_panel"] = [gx + 5, gy + 2, gz + 1]

# ---- 2d. 雷達 B：台地中央（雷達罩＋鐵塔，四周沙包、貨櫃）
bx, bz = 22, 1322
by = max(g(x, z) for x in range(bx - 4, bx + 5) for z in range(bz - 4, bz + 5))
pad(bx - 6, bz - 6, bx + 6, bz + 6, by)
sandbags(bx, bz, 9, by, gap=90)
radar_mast(bx, bz, by, 6, "radar_b")
radome(bx - 8, bz + 1, by + 1, 3)
for (dx, dz) in [(-6, -6), (6, -6), (-6, 6), (6, 6)]:
    b.box(bx + dx, by + 1, bz + dz, bx + dx, by + 3, bz + dz, conc())
c4_point("b", bx, by + 1, bz + 2)
anchors["radar_b"] = [bx, by + 1, bz]
for (cx, cz, col) in [(bx - 14, bz + 4, "green_concrete"), (bx + 12, bz - 10, "orange_terracotta")]:   # 貨櫃
    cy = max(g(x, z) for x in range(cx, cx + 6) for z in range(cz, cz + 3))
    pad(cx, cz, cx + 5, cz + 2, cy)
    b.box(cx, cy + 1, cz, cx + 5, cy + 3, cz + 2, col)
    b.box(cx + 1, cy + 1, cz + 1, cx + 4, cy + 2, cz + 1, "air")
    b.box(cx, cy + 1, cz + 1, cx, cy + 2, cz + 1, "air")

# ---- 2e. 雷達 A：北崖邊
rx, rz = 30, 1290
ry = max(g(x, z) for x in range(rx - 3, rx + 4) for z in range(rz - 3, rz + 4))
pad(rx - 4, rz - 4, rx + 4, rz + 4, ry)
sandbags(rx, rz, 6, ry, gap=180)
radar_mast(rx, rz, ry, 8, "radar_a")
c4_point("a", rx - 2, ry + 1, rz)
anchors["radar_a"] = [rx, ry + 1, rz]

# ---- 2f. 二戰舊砲堡（台地東緣，面海）＋戰壕
def casemate(cx, cz):
    """二戰舊砲堡：外層承重柱（突出）＋中層混色混凝土牆（內縮）＋裝飾層（射口裝甲板、管線、偽裝網）"""
    cy = max(g(x, z) for x in range(cx - 4, cx + 5) for z in range(cz - 3, cz + 4))
    pad(cx - 5, cz - 4, cx + 5, cz + 4, cy)
    b.box(cx - 4, cy, cz - 3, cx + 4, cy, cz + 3, "polished_andesite")
    b.walls(cx - 4, cy + 1, cz - 3, cx + 4, cy + 3, cz + 3, wall_mix)
    b.box(cx - 4, cy + 4, cz - 3, cx + 4, cy + 4, cz + 3, wall_mix)
    b.box(cx - 3, cy + 1, cz - 2, cx + 3, cy + 3, cz + 2, "air")
    for (x, z) in [(cx - 5, cz - 4), (cx + 5, cz - 4), (cx - 5, cz + 4), (cx + 5, cz + 4), (cx + 5, cz), (cx - 5, cz)]:
        b.box(x, cy, z, x, cy + 4, z, "polished_andesite")                      # 外層承重柱
    b.box(cx - 5, cy + 5, cz - 4, cx + 5, cy + 5, cz + 4, "stone_slab")            # 屋頂外伸
    b.box(cx + 4, cy + 2, cz - 2, cx + 4, cy + 2, cz + 2, "air")                  # 射口（面東）
    for z in (cz - 2, cz - 1, cz + 1, cz + 2):
        b.blocks[(cx + 5, cy + 3, z)] = "iron_trapdoor[facing=east,half=top,open=true]"   # 射口上方裝甲板
    b.box(cx - 4, cy + 1, cz, cx - 4, cy + 2, cz, "air")                          # 後門
    b.box(cx - 5, cy + 1, cz, cx - 5, cy + 2, cz, "air")
    for i in range(1, 8):                                                          # 生鏽的舊海岸砲管
        b.blocks[(cx + i, cy + 2, cz)] = "polished_basalt[axis=x]"
    b.blocks[(cx - 2, cy + 3, cz)] = "lantern[hanging=true]"
    for z in range(cz - 3, cz + 4):                                                # 外露管線
        if z != cz:
            b.blocks[(cx - 5, cy + 3, z)] = "lightning_rod[facing=south]"
    camo(cx - 4, cz - 3, cx + 4, cz + 3, cy + 6)
    for (x, z) in [(cx - 6, cz - 2), (cx - 6, cz + 2)]:
        b.blocks[(x, g(x, z) + 1, z)] = sandbag()


casemate(38, 1312)
casemate(36, 1340)
for z in range(1300, 1356):                                                  # 砲堡後方的戰壕（南北向）
    x = 26 + round(1.5 * math.sin(z / 6.0))
    for w in (0, 1):
        gy2 = g(x + w, z)
        b.blocks[(x + w, gy2, z)] = "air"
        b.blocks[(x + w, gy2 - 1, z)] = "spruce_planks" if z % 2 else "gravel"
        b.blocks[(x + w, gy2 + 1, z)] = "air"
    if z % 5 == 0:
        b.blocks[(x - 1, g(x - 1, z) + 1, z)] = sandbag()

# ---- 2g. 雷達 C：南岬燈塔（舊燈塔，頂上加裝雷達）
lx, lz = 100, 1462
ly = g(lx, lz)
pad(lx - 4, lz - 4, lx + 4, lz + 4, ly, "stone_bricks")
H_L = 22
for yy in range(ly + 1, ly + H_L):
    band = (b.rng.choice(["red_concrete", "red_concrete", "red_terracotta"]) if (yy - ly) % 8 in (6, 7)
                    else b.rng.choices(["white_concrete", "calcite", "light_gray_concrete", "white_concrete_powder"], [60, 20, 10, 10])[0])
    for dx in range(-3, 4):
        for dz in range(-3, 4):
            d = math.hypot(dx, dz)
            if 2.6 <= d <= 3.6:
                b.blocks[(lx + dx, yy, lz + dz)] = band
            elif d < 2.6:
                b.blocks[(lx + dx, yy, lz + dz)] = "air"
# 螺旋樓梯（繞中心柱）
SPIRAL = [(1, 0, "east"), (1, 1, "south"), (0, 1, "south"), (-1, 1, "west"), (-1, 0, "west"), (-1, -1, "north"), (0, -1, "north"), (1, -1, "east")]
for yy in range(ly + 1, ly + H_L):
    b.blocks[(lx, yy, lz)] = "polished_andesite"
    dx, dz, f = SPIRAL[(yy - ly) % 8]
    b.blocks[(lx + dx, yy, lz + dz)] = f"stone_brick_stairs[facing={f}]"
b.box(lx - 3, ly + H_L, lz - 3, lx + 3, ly + H_L, lz + 3, "polished_andesite")    # 燈室地板
b.box(lx - 1, ly + H_L, lz - 1, lx + 1, ly + H_L, lz + 1, "air")
for dx in range(-3, 4):
    for dz in range(-3, 4):
        if max(abs(dx), abs(dz)) == 3:
            b.blocks[(lx + dx, ly + H_L + 1, lz + dz)] = "iron_bars"
b.box(lx - 2, ly + H_L + 1, lz - 2, lx + 2, ly + H_L + 1, lz + 2, "air")
b.blocks[(lx, ly + H_L + 1, lz)] = "polished_andesite"
b.box(lx - 3, ly + H_L + 5, lz - 3, lx + 3, ly + H_L + 5, lz + 3, "dark_prismarine_slab")
for (dx, dz) in [(-3, -3), (3, -3), (-3, 3), (3, 3)]:
    b.box(lx + dx, ly + H_L + 1, lz + dz, lx + dx, ly + H_L + 4, lz + dz, "polished_basalt")
b.box(lx - 3, ly + 1, lz, lx - 3, ly + 2, lz, "air")                        # 西側入口
radar_mast(lx, lz, ly + H_L + 5, 4, "radar_c")
c4_point("c", lx + 1, ly + H_L + 1, lz)
anchors["radar_c"] = [lx, ly + H_L + 1, lz]
anchors["lighthouse_door"] = [lx - 4, ly + 1, lz]
anchors["lighthouse_sniper"] = [lx - 2, ly + H_L + 1, lz + 2]

# ---- 2h. 懸崖觀測站（北端，章節終點）
ox_, oz_ = 22, 1266
oy_ = max(g(x, z) for x in range(ox_ - 3, ox_ + 4) for z in range(oz_ - 3, oz_ + 4))
pad(ox_ - 3, oz_ - 3, ox_ + 3, oz_ + 3, oy_)
b.walls(ox_ - 3, oy_ + 1, oz_ - 3, ox_ + 3, oy_ + 3, oz_ + 3, "light_gray_concrete")
b.box(ox_ - 2, oy_ + 1, oz_ - 2, ox_ + 2, oy_ + 3, oz_ + 2, "air")
b.box(ox_ - 3, oy_ + 2, oz_ - 1, ox_ - 3, oy_ + 2, oz_ + 1, "glass_pane[north=true,south=true]")
b.box(ox_ + 3, oy_ + 2, oz_ - 2, ox_ + 3, oy_ + 2, oz_ + 2, "glass_pane[north=true,south=true]")
b.box(ox_, oy_ + 1, oz_ + 3, ox_, oy_ + 2, oz_ + 3, "air")
b.box(ox_ - 3, oy_ + 4, oz_ - 3, ox_ + 3, oy_ + 4, oz_ + 3, "gray_concrete")
for yy in range(oy_ + 5, oy_ + 12):
    b.blocks[(ox_ + 2, yy, oz_ - 2)] = "lightning_rod" if yy == oy_ + 11 else "iron_bars"
b.blocks[(ox_ + 2, oy_ + 1, oz_ - 2)] = "loom"
anchors["observation_post"] = [ox_, oy_ + 1, oz_]

# ---- 2h2. 散佈的模組化零件
for (x, z, f) in [(30, 1300, "east"), (16, 1316, "west"), (52, 1366, "south"), (36, 1366, "south"), (62, 1420, "east"), (95, 1455, "north")]:
    mg_nest(x, z, f)
for (x, z) in [(12, 1330), (40, 1296), (60, 1436)]:
    generator_set(x, z)
for (x, z) in [(26, 1316), (18, 1332), (48, 1376), (58, 1424), (34, 1286), (98, 1458)]:
    ammo_stack(x, z)
for (x, z) in [(24, 1306), (24, 1338), (44, 1380), (64, 1410), (30, 1276), (92, 1466)]:
    light_pole(x, z)
wire(18, 1378, 36, 1376)
wire(52, 1376, 60, 1372)
wire(46, 1396, 66, 1404)
for (x, z) in [(8, 1340), (4, 1324)]:
    wire(x, z, x, z + 10)
for (x, z) in b.rng.sample(beach_cells, 6):                    # 沙灘上的反登陸拒馬
    hedgehog(x, z)

# ---- 2i. 山體裂縫（西側雪山面海的那一側，結尾短暫透出藍光）
anchors["mountain_crack"] = [4, 150, 1430]

# ---- 2j. 沙灘、信標與敵人出生點
beach_mid = beach_cells[len(beach_cells) // 3]
anchors["beacon"] = [beach_mid[0] + 2, SEA + 2, beach_mid[1]]
anchors["drop_center"] = [beach_mid[0] + 10, 185, beach_mid[1]]     # 跳傘起點（海面上空）
anchors["path_bottom"] = [px0, SEA + 2, PZ]
anchors["path_top"] = list(PATH_TOP)
anchors["enemy_spawns"] = {
    "shelf_south": [60, 1446], "plateau_west": [-4, 1320], "plateau_north": [10, 1278],
    "gate_inside": [44, 1360], "south_cape": [88, 1470],
}
anchors["box"] = [X1, Z1, X2, Z2]

# ================================================================ 輸出
FN = ROOT / "datapack/longnight/data/ln/functions/build"
FN.mkdir(parents=True, exist_ok=True)
(FN / "coast_terrain.mcfunction").write_text(
    "# 由 generators/blackstone_coast.py 自動產生：地形改造（只需要跑一次，會改動天然地形）\n" + "\n".join(terrain_cmds) + "\n", encoding="utf-8")
b.pre.insert(0, "kill @e[tag=ln_coast]")
n = b.write(FN / "coast_battery.mcfunction", "# 由 generators/blackstone_coast.py 自動產生：黑石海岸砲台建築（execute positioned 0 0 0 執行）")
(ROOT / "generators/out/blackstone_coast.json").write_text(json.dumps(anchors, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"coast_terrain：{len(terrain_cmds)} 行；coast_battery：{n} 行")
print(json.dumps({k: v for k, v in anchors.items() if k != 'enemy_spawns'}, ensure_ascii=False))
