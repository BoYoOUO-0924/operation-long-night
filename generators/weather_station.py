"""第五章：廢棄高山氣象站「7 號站」生成器（第 2 版：灰白水泥、空間加大）。

參考真實高山／極地氣象站的組成，簡化成：
  1. 主樓（觀測、通訊、生活）    2. 車庫（雪地履帶車）    3. 探空氣球施放棚
  4. 觀測場（百葉箱、雨量計、積雪尺、風速計）    5. 柴油發電小屋 + 油槽
  6. 無線電天線塔                7. 屋頂瞭望塔

執行：python generators/weather_station.py
輸出：datapack/longnight/data/ln/functions/build/weather_station.mcfunction
      generators/out/weather_station.json（劇情錨點的絕對座標）
局部座標：x 往東、z 往南、y=0 是地板；原點是主樓西北角。
"""
import json
import math
from pathlib import Path

from canvas import Canvas

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = (100, 136, 948)

c = Canvas(seed=7)

# ================================================================ 調色盤（灰白水泥，低對比）
wall = c.pick([("light_gray_concrete", 88), ("light_gray_concrete_powder", 9), ("stone", 3)])
base = c.pick([("stone_bricks", 75), ("cracked_stone_bricks", 25)])
inner = c.pick([("white_concrete", 85), ("white_concrete_powder", 15)])
TRIM = "polished_andesite"
ROOF = "light_gray_concrete"
WOOD = c.pick([("spruce_planks", 90), ("dark_oak_planks", 10)])

# 主樓與附屬建築範圍（x1, x2, z1, z2）
MAIN = (0, 34, 0, 20)
GARAGE = (34, 46, 0, 13)
H = 6          # 屋頂（=天花板）高度；室內淨高 y1..5
PAD = (-12, 58, -12, 40)   # 整平的平台範圍
BLEND = 12                  # 平台外圍與山坡融合的寬度


# ================================================================ 整地：平台 + 與地形融合的斜坡
def terrain():
    x1, x2, z1, z2 = PAD
    # 平台本體（分兩段避免超過 fill 上限）
    for a in range(x1, x2 + 1, 16):
        b = min(a + 15, x2)
        c.pre.append(f"fill ~{a} ~1 ~{z1} ~{b} ~24 ~{z2} air")
        c.pre.append(f"fill ~{a} ~-10 ~{z1} ~{b} ~-1 ~{z2} stone replace air")
    c.pre.append(f"fill ~{x1} ~0 ~{z1} ~{x2} ~0 ~{z2} snow_block")
    # 外圍：把地形夾在「上斜面」與「下斜面」之間，切掉懸崖、填平落差
    hmap = {}
    for x in range(x1 - BLEND, x2 + BLEND + 1):
        for z in range(z1 - BLEND, z2 + BLEND + 1):
            dx = max(x1 - x, 0, x - x2)
            dz = max(z1 - z, 0, z - z2)
            d = math.hypot(dx, dz)
            if 0 < d <= BLEND:
                hmap[(x, z)] = max(1, round(d * 0.8))
    rows = {}
    for (x, z), h in hmap.items():
        rows.setdefault((z, h), []).append(x)
    for (z, h), xs in rows.items():
        xs.sort()
        start = prev = xs[0]
        for x in xs[1:] + [None]:
            if x is not None and x == prev + 1:
                prev = x
                continue
            c.pre += [
                f"fill ~{start} ~{h + 1} ~{z} ~{prev} ~28 ~{z} air",                       # 削掉上方
                f"fill ~{start} ~{h} ~{z} ~{prev} ~{h} ~{z} snow_block replace #minecraft:base_stone_overworld",
                f"fill ~{start} ~{h} ~{z} ~{prev} ~{h} ~{z} snow_block replace #minecraft:dirt",
                f"fill ~{start} ~-16 ~{z} ~{prev} ~{-h - 1} ~{z} stone replace air",          # 填下方
                f"fill ~{start} ~{-h} ~{z} ~{prev} ~{-h} ~{z} snow_block replace air",
            ]
            if x is not None:
                start = prev = x


terrain()
c.pre.append("kill @e[tag=ln_deco]")


# ================================================================ 小工具
def pane(axis):
    return "glass_pane[east=true,west=true]" if axis == "x" else "glass_pane[north=true,south=true]"


def window(x, z, axis, width=2, y1=2, y2=4):
    """在外牆開窗：axis='x' 表示牆沿 x 方向延伸。"""
    for i in range(width):
        px, pz = (x + i, z) if axis == "x" else (x, z + i)
        for y in range(y1, y2 + 1):
            broken = c.chance(0.12)
            c.set(px, y, pz, "air" if broken else pane(axis))


def frame(x, y, z, facing, item):
    f = {"north": 2, "south": 3, "west": 4, "east": 5}[facing]
    c.post.append(f'summon item_frame ~{x}.5 ~{y}.5 ~{z}.5 {{Facing:{f}b,Fixed:1b,Invulnerable:1b,'
                  f'Item:{{id:"minecraft:{item}",Count:1b}},Tags:["ln_deco"]}}')


def lamp(x, z, y=H - 1, p=0.8):
    c.set(x, y, z, "lantern[hanging=true]" if c.chance(p) else "chain[axis=y]")


def building(x1, x2, z1, z2, h=H, floor=WOOD):
    c.box(x1, 0, z1, x2, 0, z2, floor)
    c.walls(x1, 1, z1, x2, 1, z2, base)
    c.walls(x1, 2, z1, x2, h - 1, z2, wall)
    for x, z in [(x1, z1), (x2, z1), (x1, z2), (x2, z2)]:
        c.box(x, 1, z, x, h, z, TRIM)
    c.box(x1, h, z1, x2, h, z2, ROOF)
    # 屋簷收邊 + 女兒牆 + 積雪
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            if x in (x1, x2) or z in (z1, z2):
                c.set(x, h + 1, z, "stone_brick_wall" if c.chance(0.85) else "polished_andesite")
            elif c.chance(0.75):
                c.set(x, h + 1, z, f"snow[layers={c.rng.randint(1, 3)}]")


# ================================================================ 1. 主樓
X1, X2, Z1, Z2 = MAIN
building(X1, X2, Z1, Z2)
CZ1, CZ2 = 9, 11                          # 走廊（3 格寬）
c.box(X1 + 1, 0, CZ1, X2 - 1, 0, CZ2, "polished_andesite")
c.box(X1 + 1, 1, CZ1 - 1, X2 - 1, H - 1, CZ1 - 1, inner)   # 北側房間牆
c.box(X1 + 1, 1, CZ2 + 1, X2 - 1, H - 1, CZ2 + 1, inner)   # 南側房間牆
# 北側：通訊室 x1..10 | 預報室 x12..21 | 鍋爐廳 x23..33
c.box(11, 1, 1, 11, H - 1, CZ1 - 1, inner)
c.box(22, 1, 1, 22, H - 1, CZ1 - 1, inner)
# 南側：寢室 x1..12 | 餐廳廚房 x14..24 | 醫務儲藏 x26..33
c.box(13, 1, CZ2 + 1, 13, H - 1, Z2 - 1, inner)
c.box(25, 1, CZ2 + 1, 25, H - 1, Z2 - 1, inner)
# 門洞（不裝門，NPC 和玩家都能自由通過）
for (x, z) in [(5, CZ1 - 1), (6, CZ1 - 1), (16, CZ1 - 1), (17, CZ1 - 1), (27, CZ1 - 1), (28, CZ1 - 1),
               (6, CZ2 + 1), (7, CZ2 + 1), (18, CZ2 + 1), (19, CZ2 + 1), (29, CZ2 + 1), (30, CZ2 + 1)]:
    c.box(x, 1, z, x, 3, z, "air")
c.box(X1, 1, CZ1, X1, 3, CZ2, "air")      # 西側大門（3 格寬）
c.box(X1, 4, CZ1, X1, 4, CZ2, TRIM)
c.box(18, 1, Z2, 19, 3, Z2, "air")        # 南門（往觀測場）
c.box(X2, 1, CZ1, X2, 3, CZ2, "air")      # 走廊 → 車庫
# 外牆窗戶（2 格寬 × 3 格高）
for x in (3, 8, 14, 19, 25, 30):
    window(x, Z1, "x")
for x in (3, 9, 15, 22, 27, 31):
    if not 18 <= x <= 19:
        window(x, Z2, "x")
for z in (3, 15):
    window(X1, z, "z")
# 走廊吊燈
for x in range(3, X2, 6):
    lamp(x, 10)

# ---- 通訊室（x1..10, z1..8）：狐狸修掃描器的地方
c.box(1, 0, 1, 10, 0, 7, WOOD)
for x in range(2, 10):                                    # 北牆設備架
    c.set(x, 1, 1, "gray_concrete")
    c.set(x, 2, 1, "black_concrete" if x % 2 else "gray_concrete")
    c.set(x, 3, 1, "gray_concrete")
for x, b in [(2, "stone_button[face=wall,facing=south]"), (3, "lever[face=wall,facing=south]"),
             (5, "stone_button[face=wall,facing=south]"), (6, "tripwire_hook[facing=south]"),
             (8, "lever[face=wall,facing=south]"), (9, "stone_button[face=wall,facing=south]")]:
    c.set(x, 2, 2, b)
frame(4, 2, 2, "south", "compass")
frame(7, 2, 2, "south", "clock")
frame(4, 3, 2, "south", "map")
c.box(3, 1, 5, 7, 1, 5, "dark_oak_slab[type=top]")       # 中央工作桌
c.set(4, 2, 5, "daylight_detector")
c.set(6, 2, 5, "redstone_lamp")
c.set(5, 1, 6, "spruce_stairs[facing=north]")
c.set(9, 1, 6, "smithing_table")                          # 狐狸的維修台
c.set(9, 1, 7, "barrel[facing=up]")
c.set(1, 1, 7, "chiseled_bookshelf[facing=east]")
c.box(1, 1, 1, 1, H, 1, "ladder[facing=south]")           # 爬梯 → 瞭望塔
lamp(5, 4)

# ---- 預報室（x12..21, z1..8）
c.box(12, 0, 1, 21, 0, 7, WOOD)
c.box(14, 1, 3, 19, 1, 5, "spruce_slab[type=top]")        # 大地圖桌
c.set(16, 2, 4, "cartography_table")
for x in (14, 19):
    c.set(x, 1, 2, "spruce_stairs[facing=south]")
    c.set(x, 1, 6, "spruce_stairs[facing=north]")
for x in range(12, 22):                                   # 北牆書架
    c.set(x, 1, 1, "bookshelf" if x % 3 else "chiseled_bookshelf[facing=south]")
for x in (13, 16, 20):
    frame(x, 3, 1 + 1, "south", "clock")                  # 氣壓計／時鐘牆
c.set(21, 1, 7, "brewing_stand")
c.set(12, 1, 7, "lectern[facing=east]")
lamp(16, 4)

# ---- 鍋爐廳（x23..33, z1..8）：地熱鍋爐
c.box(23, 0, 1, 33, 0, 8, "polished_andesite")
bx, bz = 28, 4
c.box(bx - 2, 1, bz - 2, bx + 2, 1, bz + 2, "iron_block")
c.box(bx - 1, 1, bz - 1, bx + 1, 1, bz + 1, "magma_block")
c.box(bx - 1, 2, bz - 1, bx + 1, 4, bz + 1, "waxed_weathered_copper")
c.set(bx, 2, bz + 2, "blast_furnace[facing=south,lit=true]")
c.set(bx - 1, 2, bz + 2, "iron_trapdoor[facing=south,half=top,open=true]")
c.set(bx + 1, 2, bz + 2, "iron_trapdoor[facing=south,half=top,open=true]")
c.set(bx, 5, bz, "lightning_rod[facing=up]")
for x in range(23, 34):                                   # 天花板水平管線
    c.set(x, 5, 2, "lightning_rod[facing=east]")
    c.set(x, 5, 7, "lightning_rod[facing=east]")
for z in range(2, 8):
    c.set(33 - 1, 4, z, "lightning_rod[facing=south]")
c.box(24, 1, 1, 24, 4, 1, "chain[axis=y]")
frame(bx - 1, 3, bz + 2, "south", "clock")                # 壓力錶
c.set(32, 1, 1, "barrel[facing=up]")
c.set(23, 1, 8, "cauldron")
c.set(26, 0, 8, "magma_block")                            # 地上的熱裂縫
c.set(31, 0, 6, "magma_block")
lamp(25, 7)
lamp(31, 2)

# ---- 寢室（x1..12, z13..19）：上下鋪
c.box(1, 0, 13, 12, 0, 19, WOOD)
for x in (2, 5, 8, 11):
    c.set(x, 1, 18, "gray_bed[facing=north,part=foot]")
    c.set(x, 1, 19, "gray_bed[facing=north,part=head]")
    c.box(x, 2, 18, x, 2, 19, "spruce_slab[type=top]")
    c.set(x, 3, 18, "gray_bed[facing=north,part=foot]")
    c.set(x, 3, 19, "gray_bed[facing=north,part=head]")
    c.set(x, 1, 14, "barrel[facing=south]")
    c.set(x, 2, 14, "barrel[facing=south]")
c.set(12, 1, 16, "furnace[facing=west]")
lamp(6, 16)

# ---- 餐廳廚房（x14..24, z13..19）
c.box(14, 0, 13, 24, 0, 19, WOOD)
c.box(16, 1, 15, 21, 1, 16, "spruce_slab[type=top]")
for x in (16, 18, 20):
    c.set(x, 1, 14, "spruce_stairs[facing=south]")
    c.set(x, 1, 17, "spruce_stairs[facing=north]")
for z, b in [(14, "smoker[facing=west]"), (15, "furnace[facing=west]"), (16, "barrel[facing=west]"),
             (17, "cauldron"), (18, "barrel[facing=west]")]:
    c.set(24, 1, z, b)
c.box(24, 2, 14, 24, 2, 18, "spruce_slab[type=bottom]")
lamp(19, 16)

# ---- 醫務／儲藏（x26..33, z13..19）
c.box(26, 0, 13, 33, 0, 19, "polished_andesite")
c.set(27, 1, 18, "white_bed[facing=north,part=foot]")
c.set(27, 1, 19, "white_bed[facing=north,part=head]")
c.set(29, 1, 19, "brewing_stand")
for x in range(30, 34):
    for y in (1, 2):
        c.set(x, y, 13 + (x % 2), "barrel[facing=north]")
lamp(29, 16)

# ================================================================ 2. 車庫（x34..46, z0..13）
gx1, gx2, gz1, gz2 = GARAGE
c.box(gx1 + 1, 0, gz1, gx2, 0, gz2, c.pick([("stone", 50), ("gravel", 20), ("cobblestone", 30)]))
c.walls(gx1, 1, gz1, gx2, 1, gz2, base)
c.walls(gx1, 2, gz1, gx2, H - 1, gz2, wall)
c.box(gx1 + 1, H, gz1, gx2, H, gz2, ROOF)
for x in range(gx1, gx2 + 1):
    for z in range(gz1, gz2 + 1):
        if x == gx2 or z in (gz1, gz2):
            c.set(x, H + 1, z, "stone_brick_wall")
        elif x > gx1 and c.chance(0.75):
            c.set(x, H + 1, z, f"snow[layers={c.rng.randint(1, 3)}]")
c.box(gx1, 1, CZ1, gx1, 3, CZ2, "air")                     # 與走廊相通
c.box(gx2, 1, 3, gx2, 4, 8, "air")                         # 東側大門（鐵捲門被撞開）
c.box(gx2, 5, 3, gx2, 5, 8, "iron_trapdoor[facing=east,half=top,open=false]")
c.set(gx2, 1, 3, "iron_bars[north=true,south=true]")
window(38, gz1, "x")
window(41, gz2, "x")
# 雪地履帶車
c.box(37, 1, 3, 43, 1, 3, "black_concrete")
c.box(37, 1, 7, 43, 1, 7, "black_concrete")
c.box(37, 1, 4, 43, 1, 6, "gray_concrete")
c.box(37, 2, 3, 43, 3, 7, "orange_concrete")
c.box(41, 3, 3, 43, 4, 7, "orange_concrete")
c.box(42, 4, 3, 43, 4, 7, "light_blue_stained_glass")
c.box(41, 4, 4, 41, 4, 6, "light_blue_stained_glass")
c.box(37, 4, 4, 40, 4, 6, "gray_concrete")
c.set(43, 3, 4, "redstone_lamp")
c.set(43, 3, 6, "redstone_lamp")
# 工作台、物資、零件箱（玩家要按的按鈕）
c.box(gx1 + 1, 1, 12, gx1 + 4, 1, 12, "barrel[facing=north]")
c.set(36, 1, 1, "anvil[facing=east]")
c.set(37, 1, 1, "grindstone[face=floor,facing=north]")
c.set(44, 1, 12, "chest[facing=north]")
c.set(44, 2, 12, "stone_button[face=floor,facing=north]")
c.set(45, 1, 12, "barrel[facing=up]")
lamp(40, 10)
lamp(40, 2, p=0.5)

# ================================================================ 3. 瞭望塔（主樓西北角屋頂，白鴉的狙擊點）
tx1, tx2, tz1, tz2 = 0, 7, 0, 7
ty = H + 1
c.walls(tx1, ty, tz1, tx2, ty + 4, tz2, wall)
for x, z in [(tx1, tz1), (tx2, tz1), (tx1, tz2), (tx2, tz2)]:
    c.box(x, ty, z, x, ty + 4, z, TRIM)
c.box(tx1 + 1, ty, tz1 + 1, tx2 - 1, ty + 4, tz2 - 1, "air")
for i in range(2, 6):
    for y in (ty + 1, ty + 2):
        c.set(i, y, tz1, pane("x"))
        c.set(i, y, tz2, pane("x"))
        c.set(tx1, y, i, pane("z"))
        c.set(tx2, y, i, pane("z"))
c.box(tx1, ty + 5, tz1, tx2, ty + 5, tz2, ROOF)
for x in range(tx1, tx2 + 1):
    for z in range(tz1, tz2 + 1):
        if x in (tx1, tx2) or z in (tz1, tz2):
            c.set(x, ty + 6, z, "stone_brick_wall")
c.box(tx2, ty, 3, tx2, ty + 1, 4, "air")                   # 通往屋頂的門洞
c.set(1, H, 1, "ladder[facing=south]")
c.set(1, ty, 1, "ladder[facing=south]")
c.set(4, ty + 4, 4, "lantern[hanging=true]")
c.box(3, ty + 6, 3, 3, ty + 12, 3, "iron_bars")            # 天線
c.set(3, ty + 13, 3, "red_concrete")
c.set(3, ty + 14, 3, "redstone_torch")
for (x, z) in [(5, 2), (5, 5)]:
    c.set(x, ty + 6, z, "daylight_detector")

# 主樓屋頂設備：排煙、通風口
c.set(28, H + 1, 4, "campfire[lit=true,signal_fire=false]")
for (x, z) in [(14, 4), (20, 16), (8, 15)]:
    c.set(x, H + 1, z, "iron_bars")
    c.set(x, H + 2, z, "iron_trapdoor[half=bottom,open=false]")

# ================================================================ 4. 探空氣球施放棚（東南，x38..45, z22..30）
sx1, sx2, sz1, sz2 = 38, 45, 22, 30
building(sx1, sx2, sz1, sz2, h=8, floor="polished_andesite")
c.box(sx1 + 2, 1, sz1, sx2 - 2, 6, sz1, "air")             # 北側挑高大門
c.box(sx1 + 2, 7, sz1, sx2 - 2, 7, sz1, TRIM)
c.set(41, 1, 28, "cauldron")                                # 氫氣產生器（簡化）
c.box(43, 1, 28, 44, 2, 29, "iron_block")
c.set(39, 1, 29, "barrel[facing=up]")
c.set(42, 3, 26, "white_wool")                              # 掛著的氣球
c.set(42, 4, 26, "white_wool")
c.box(41, 3, 26, 41, 4, 26, "white_wool")
c.box(42, 5, 26, 42, 7, 26, "chain[axis=y]")
lamp(41, 24, y=7)

# ================================================================ 5. 觀測場（西南，x2..14, z25..35，圍欄）
ox1, ox2, oz1, oz2 = 2, 14, 25, 35
for x in range(ox1, ox2 + 1):
    for z in range(oz1, oz2 + 1):
        if x in (ox1, ox2):
            c.set(x, 1, z, "spruce_fence[north=true,south=true]")
        elif z in (oz1, oz2):
            c.set(x, 1, z, "spruce_fence[east=true,west=true]")
c.set(8, 1, oz1, "spruce_fence_gate[facing=north,open=true]")
for (x, z) in [(4, 28), (7, 28)]:                            # 兩座百葉箱
    for dx, dz in [(0, 0), (1, 0), (0, 1), (1, 1)]:
        c.box(x + dx, 1, z + dz, x + dx, 2, z + dz, "spruce_fence")
    c.box(x, 3, z, x + 1, 4, z + 1, "white_concrete")
    c.set(x, 3, z - 1, "birch_trapdoor[facing=north,half=bottom,open=true]")
    c.box(x, 5, z, x + 1, 5, z + 1, "smooth_stone_slab")
c.set(11, 1, 28, "cauldron")                                 # 雨量計
c.box(11, 1, 32, 11, 4, 32, "birch_fence")                   # 積雪尺
c.set(11, 5, 32, "red_concrete")
c.box(5, 1, 33, 5, 7, 33, "spruce_fence")                    # 風速計／風向標
c.set(5, 8, 33, "lightning_rod[facing=up]")
for dx, dz in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
    c.set(5 + dx, 7, 33 + dz, "cobblestone_wall")

# ================================================================ 6. 柴油發電小屋 + 油槽（主樓南側，x24..32, z24..30）
building(24, 30, 25, 30, h=5, floor="polished_andesite")
c.box(27, 1, 25, 27, 3, 25, "air")
c.box(25, 1, 27, 29, 2, 28, "iron_block")
c.set(26, 3, 27, "lightning_rod[facing=up]")
c.set(30, 6, 28, "campfire[lit=false,signal_fire=false]")
for zc in (33, 37):                                          # 圓筒油槽（側躺）
    for x in range(22, 31):
        for (dy, dz) in [(1, 0), (2, 0), (1, 1), (2, 1), (1, -1), (2, -1), (3, 0)]:
            c.set(x, dy, zc + dz, "iron_block")
        c.set(x, 3, zc - 1, "iron_trapdoor[facing=south,half=bottom,open=false]")
        c.set(x, 3, zc + 1, "iron_trapdoor[facing=north,half=bottom,open=false]")
    c.box(22, 1, zc - 1, 22, 3, zc + 1, "light_gray_concrete")
    c.box(30, 1, zc - 1, 30, 3, zc + 1, "light_gray_concrete")

# ================================================================ 7. 天線塔（東北，x52, z-4）
mx, mz = 52, -4
c.box(mx, 1, mz, mx, 26, mz, "iron_bars")
for y in (8, 16, 24):
    c.set(mx, y, mz, "red_concrete")
c.set(mx, 27, mz, "red_concrete")
c.set(mx, 28, mz, "redstone_torch")
for dx, dz in [(4, 0), (-4, 0), (0, 4), (0, -4)]:          # 拉索地錨
    c.set(mx + dx, 1, mz + dz, "cobblestone_wall")

# ================================================================ 院子積雪、牆邊雪堆
built = set()
for (x, y, z) in c.blocks:
    if y >= 1:
        built.add((x, z))
for x in range(PAD[0], PAD[1] + 1):
    for z in range(PAD[2], PAD[3] + 1):
        if (x, z) in built:
            continue
        near_wall = any((x + dx, z + dz) in built for dx, dz in [(1, 0), (-1, 0), (0, 1), (0, -1)])
        windward = z < 3 or x < 3                    # 北風、西風吹來的一側雪比較厚
        if near_wall and windward and c.chance(0.85):
            c.set(x, 1, z, f"snow[layers={c.rng.randint(4, 7)}]")
        elif near_wall and c.chance(0.6):
            c.set(x, 1, z, f"snow[layers={c.rng.randint(2, 4)}]")
        elif c.chance(0.5):
            c.set(x, 1, z, f"snow[layers={c.rng.randint(1, 2)}]")

# 告示牌（車庫大門旁）
c.post.append(
    f"setblock ~{gx2 + 1} ~3 ~2 spruce_wall_sign[facing=east]"
    "{front_text:{messages:['{\"text\":\"МЕТЕОСТАНЦИЯ\"}','{\"text\":\"№ 7\"}','{\"text\":\"高山氣象站 7 號\"}','{\"text\":\"\"}']}}"
)

# ================================================================ 輸出
out_fn = ROOT / "datapack/longnight/data/ln/functions/build/weather_station.mcfunction"
n = c.write(out_fn, "# 由 generators/weather_station.py 自動產生，請勿手動修改")


def a(x, y, z):
    return [ORIGIN[0] + x, ORIGIN[1] + y, ORIGIN[2] + z]


anchors = {
    "origin": list(ORIGIN),
    "pad": [ORIGIN[0] + PAD[0] - BLEND, ORIGIN[2] + PAD[2] - BLEND, ORIGIN[0] + PAD[1] + BLEND, ORIGIN[2] + PAD[3] + BLEND],
    "garage_door_outside": a(49, 1, 6),
    "fox_bench": a(9, 1, 6),
    "tank_radio": a(6, 1, 7),
    "officer_radio": a(4, 1, 6),
    "baiya_tower": a(4, ty, 4),
    "parts_button": a(44, 2, 12),
    "checkpoint": a(20, 1, 10),
    "boiler": a(bx, 1, bz),
    "viewpoint": a(70, 18, 48),
    "start_center": [178, 958],
    "enemy_spawns": {
        "east": [ORIGIN[0] + 82, ORIGIN[2] + 8],
        "north": [ORIGIN[0] + 18, ORIGIN[2] - 36],
        "south": [ORIGIN[0] + 18, ORIGIN[2] + 62],
        "west": [ORIGIN[0] - 34, ORIGIN[2] + 10],
    },
}
(ROOT / "generators/out").mkdir(exist_ok=True)
(ROOT / "generators/out/weather_station.json").write_text(json.dumps(anchors, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"weather_station.mcfunction：{n} 行指令；原點 {ORIGIN}")
