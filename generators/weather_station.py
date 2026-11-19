"""第五章：廢棄高山氣象站「7 號站」生成器。

執行：python generators/weather_station.py
輸出：
  datapack/longnight/data/ln/functions/build/weather_station.mcfunction（建築本體，相對座標）
  generators/out/weather_station.json（原點與劇情錨點的絕對座標）

原點（西北角地板）放在雪坡平台 ORIGIN。玩家從東邊山下走上來，由東側車庫進站。
局部座標：x 往東、z 往南、y=0 是地板。
"""
import json
from pathlib import Path

from canvas import Canvas

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = (106, 136, 952)

c = Canvas(seed=1993)

# ---------------------------------------------------------------- 調色盤（風化）
plaster = c.pick([("smooth_stone", 40), ("light_gray_concrete", 30), ("andesite", 15), ("polished_andesite", 15)])
base = c.pick([("stone_bricks", 55), ("cracked_stone_bricks", 30), ("cobblestone", 15)])
inner = c.pick([("smooth_stone", 60), ("polished_andesite", 25), ("light_gray_concrete", 15)])
garage = c.pick([("cobblestone", 35), ("stone_bricks", 35), ("cracked_stone_bricks", 20), ("mossy_cobblestone", 3), ("andesite", 7)])
roof = c.pick([("gray_concrete", 70), ("cyan_terracotta", 15), ("light_gray_concrete", 15)])
planks = c.pick([("spruce_planks", 80), ("dark_oak_planks", 20)])

MAIN = (0, 21, 0, 15)      # x1, x2, z1, z2（主樓）
ANNEX = (21, 29, 0, 10)    # 車庫，與主樓共用 x=21 這面牆
H = 5                      # 屋頂高度

# ---------------------------------------------------------------- 整地
c.pre += [
    "fill ~-8 ~1 ~-8 ~37 ~18 ~28 air",
    "fill ~-8 ~0 ~-8 ~37 ~0 ~28 snow_block",
    "fill ~-8 ~-1 ~-8 ~37 ~-8 ~28 stone replace air",
    "fill ~-8 ~-1 ~-8 ~37 ~-8 ~28 stone replace snow",
]


def pane_x():  # 東西向牆上的窗（玻璃沿 x 方向連接）
    r = c.rng.random()
    if r < 0.25:
        return "air"
    if r < 0.45:
        return "white_stained_glass_pane[east=true,west=true]"
    return "glass_pane[east=true,west=true]"


def pane_z():
    r = c.rng.random()
    if r < 0.25:
        return "air"
    if r < 0.45:
        return "white_stained_glass_pane[north=true,south=true]"
    return "glass_pane[north=true,south=true]"


# ---------------------------------------------------------------- 主樓外殼
x1, x2, z1, z2 = MAIN
c.box(x1, 0, z1, x2, 0, z2, planks)                       # 地板
c.walls(x1, 1, z1, x2, 1, z2, base)                       # 牆腳
c.walls(x1, 2, z1, x2, H - 1, z2, plaster)                # 牆身
for x, z in [(x1, z1), (x2, z1), (x1, z2), (x2, z2)]:
    c.box(x, 1, z, x, H - 1, z, "polished_andesite")      # 轉角柱
c.box(x1, H, z1, x2, H, z2, roof)                         # 主樓平屋頂
c.box(ANNEX[0], H, ANNEX[2], ANNEX[1], H, ANNEX[3], roof)  # 車庫屋頂

# 窗戶（y=2..3）
for x in range(x1 + 2, x2 - 1, 3):
    for z in (z1, z2):
        c.box(x, 2, z, x, 3, z, pane_x)
for z in range(z1 + 2, z2 - 1, 3):
    c.box(x1, 2, z, x1, 3, z, pane_z)

# ---------------------------------------------------------------- 內部隔間
# 走廊 z=8..9；北側房間 z=1..6，南側房間 z=11..14
c.box(x1 + 1, 1, 7, x2 - 1, H - 1, 7, inner)
c.box(x1 + 1, 1, 10, x2 - 1, H - 1, 10, inner)
c.box(9, 1, 1, 9, H - 1, 6, inner)          # 無線電室 | 鍋爐室
c.box(11, 1, 11, 11, H - 1, 14, inner)      # 寢室 | 餐廳
c.box(x1 + 1, 0, 8, x2 - 1, 0, 9, "gray_concrete")       # 走廊地板
c.box(10, 0, 1, x2 - 1, 0, 6, "polished_andesite")       # 鍋爐室地板

# 房門（門洞 + 木門）
def door(x, z, facing):
    c.set(x, 1, z, f"spruce_door[facing={facing},half=lower,hinge=left,open=false]")
    c.set(x, 2, z, f"spruce_door[facing={facing},half=upper,hinge=left,open=false]")


for (x, z, f) in [(5, 7, "south"), (15, 7, "south"), (5, 10, "north"), (16, 10, "north")]:
    door(x, z, f)
# 西側大門（雙開，兩扇都開著——門被風吹開）
c.set(x1, 1, 8, "spruce_door[facing=east,half=lower,hinge=left,open=true]")
c.set(x1, 2, 8, "spruce_door[facing=east,half=upper,hinge=left,open=true]")
c.set(x1, 1, 9, "spruce_door[facing=east,half=lower,hinge=right,open=true]")
c.set(x1, 2, 9, "spruce_door[facing=east,half=upper,hinge=right,open=true]")
c.box(x1, 3, 8, x1, 3, 9, "spruce_planks")
# 南側門（餐廳）
c.set(16, 1, z2, "spruce_door[facing=north,half=lower,hinge=left,open=false]")
c.set(16, 2, z2, "spruce_door[facing=north,half=upper,hinge=left,open=false]")

# 吊燈：走廊與各房間（部分壞掉）
for (x, z) in [(3, 8), (8, 9), (13, 8), (18, 9), (4, 3), (14, 3), (18, 4), (5, 12), (16, 12)]:
    c.set(x, H - 1, z, "lantern[hanging=true]" if c.chance(0.8) else "chain[axis=y]")

# ---------------------------------------------------------------- 無線電室（西北，x1..8, z1..6）—— 狐狸修掃描器的地方
c.box(1, 1, 1, 8, 1, 1, "spruce_slab[type=top]")          # 北牆工作台
for x, b in [(2, "observer[facing=south]"), (3, "note_block"), (4, "redstone_lamp"),
             (5, "dispenser[facing=south]"), (6, "observer[facing=south]"), (7, "note_block")]:
    c.set(x, 2, 1, b)                                     # 無線電設備牆
c.set(4, 3, 1, "redstone_lamp")
c.set(6, 1, 4, "smithing_table")                          # 狐狸的維修台
c.set(7, 1, 4, "spruce_slab[type=top]")
c.set(3, 1, 5, "lectern[facing=north]")
c.set(8, 1, 6, "barrel[facing=up]")
# 爬梯到屋頂瞭望塔
c.box(1, 1, 1, 1, H, 1, "ladder[facing=south]")

# ---------------------------------------------------------------- 鍋爐室（東北，x10..20, z1..6）—— 地熱鍋爐
bx, bz = 15, 3
c.box(bx - 1, 1, bz - 1, bx + 1, 1, bz + 1, "iron_block")
c.set(bx, 1, bz, "magma_block")
c.box(bx - 1, 2, bz - 1, bx + 1, 3, bz + 1, "waxed_weathered_copper")
c.set(bx, 2, bz + 1, "blast_furnace[facing=south,lit=true]")
c.set(bx - 1, 2, bz + 1, "iron_trapdoor[facing=south,half=top,open=true]")
c.set(bx, 4, bz, "lightning_rod[facing=up]")
for x in range(10, 21):                                    # 天花板管線
    c.set(x, H - 1, 1, "iron_bars[east=true,west=true]")
for x in (11, 19):
    c.box(x, 1, 1, x, H - 1, 1, "chain[axis=y]")
c.set(11, 1, 6, "cauldron")
c.set(19, 1, 5, "barrel[facing=up]")
c.set(20, 1, 6, "barrel[facing=up]")
c.set(12, 2, 1, "lever[face=wall,facing=south]")
c.set(bx + 2, 1, bz + 2, "magma_block")                    # 地上的熱裂縫
c.set(13, 0, 5, "magma_block")

# ---------------------------------------------------------------- 寢室（西南，x1..10, z11..14）
for x in (2, 5, 8):
    c.set(x, 1, 13, "gray_bed[facing=north,part=foot]")
    c.set(x, 1, 14, "gray_bed[facing=north,part=head]")
    c.set(x, 1, 11, "barrel[facing=south]")                # 置物櫃
c.set(10, 1, 14, "furnace[facing=north]")
c.set(10, 2, 14, "flower_pot")

# ---------------------------------------------------------------- 餐廳（東南，x12..20, z11..14）
c.box(14, 1, 12, 18, 1, 13, "spruce_slab[type=top]")      # 長桌
for x in (14, 16, 18):
    c.set(x, 1, 11, "spruce_stairs[facing=south]")
    c.set(x, 1, 14, "spruce_stairs[facing=north]")
c.set(20, 1, 11, "smoker[facing=west]")
c.set(20, 1, 12, "barrel[facing=west]")
c.set(20, 1, 14, "cauldron")

# ---------------------------------------------------------------- 車庫（東側，x21..29, z0..10）—— 玩家進站入口
ax1, ax2, az1, az2 = ANNEX
c.box(ax1 + 1, 0, az1, ax2, 0, az2, c.pick([("stone", 50), ("gravel", 25), ("cobblestone", 25)]))
c.walls(ax1, 1, az1, ax2, H - 1, az2, garage)
c.box(ax1, 1, 8, ax1, 2, 9, "air")                         # 走廊 → 車庫的通道
c.box(ax2, 1, 3, ax2, 3, 7, "air")                         # 東側大門（鐵捲門被撞壞）
c.box(ax2, 4, 3, ax2, 4, 7, "iron_trapdoor[facing=east,half=top,open=false]")
c.set(ax2, 1, 3, "iron_bars[north=true,south=true]")
for z in (2, 8):                                          # 車庫窗
    c.set(ax1 + 4, 2, az1 if z == 2 else az2, pane_x())
# 雪地履帶車殘骸（簡化）
c.box(23, 1, 2, 26, 1, 5, "black_concrete")
c.box(23, 2, 2, 26, 2, 5, "orange_terracotta")
c.box(23, 3, 2, 24, 3, 5, "orange_terracotta")
c.box(25, 3, 2, 26, 3, 5, "light_blue_stained_glass")
c.set(26, 2, 2, "redstone_lamp")
# 物資箱 + 零件箱（玩家要按的按鈕）
for (x, z) in [(22, 9), (23, 9), (22, 8), (28, 9)]:
    c.set(x, 1, z, "barrel[facing=up]")
c.set(27, 1, 9, "chest[facing=north]")
c.set(27, 2, 9, "stone_button[face=floor,facing=north]")
c.set(24, 3, 9, "lantern[hanging=true]")

# ---------------------------------------------------------------- 屋頂：女兒牆、積雪、瞭望塔
roof_cells = {(x, z) for x in range(MAIN[0], MAIN[1] + 1) for z in range(MAIN[2], MAIN[3] + 1)}
roof_cells |= {(x, z) for x in range(ANNEX[0], ANNEX[1] + 1) for z in range(ANNEX[2], ANNEX[3] + 1)}
for (x, z) in roof_cells:
    edge = any((x + dx, z + dz) not in roof_cells for dx, dz in [(1, 0), (-1, 0), (0, 1), (0, -1)])
    if edge:
        c.set(x, H + 1, z, "light_gray_concrete")
    elif c.chance(0.7):
        c.set(x, H + 1, z, f"snow[layers={c.rng.randint(1, 3)}]")
# 瞭望塔（西北角，白鴉的狙擊點）
c.walls(0, H + 1, 0, 5, H + 5, 5, plaster)
for x in range(1, 5):
    c.box(x, H + 2, 0, x, H + 3, 0, pane_x)
    c.box(x, H + 2, 5, x, H + 3, 5, pane_x)
for z in range(1, 5):
    c.box(0, H + 2, z, 0, H + 3, z, pane_z)
    c.box(5, H + 2, z, 5, H + 3, z, pane_z)
c.box(0, H + 6, 0, 5, H + 6, 5, roof)
c.box(1, H + 1, 1, 4, H + 1, 4, "air")
c.set(4, H + 1, 2, "air")
c.set(5, H + 1, 3, "spruce_door[facing=east,half=lower,hinge=left,open=false]")
c.set(5, H + 2, 3, "spruce_door[facing=east,half=upper,hinge=left,open=false]")
c.set(3, H + 5, 3, "lantern[hanging=true]")
c.box(2, H + 7, 2, 2, H + 11, 2, "iron_bars")              # 天線
c.set(2, H + 12, 2, "redstone_lamp[lit=true]")
c.set(4, H + 7, 4, "lightning_rod[facing=up]")
c.set(3, H + 7, 1, "daylight_detector")
c.set(4, H + 7, 1, "daylight_detector")
# 屋頂上的通風口與儀器
for (x, z) in [(12, 4), (17, 12), (25, 6)]:
    c.set(x, H + 1, z, "iron_bars")
    c.set(x, H + 2, z, "iron_trapdoor[half=bottom,open=false]")
c.set(15, H + 1, 3, "campfire[lit=true,signal_fire=false]")   # 鍋爐排煙

# ---------------------------------------------------------------- 院子：氣象儀器、天線塔、油槽、圍欄
# 百葉箱
for (x, z) in [(3, 19), (5, 19), (3, 21), (5, 21)]:
    c.box(x, 1, z, x, 2, z, "spruce_fence")
c.box(3, 3, 19, 5, 4, 21, "white_concrete")
c.set(4, 3, 18, "birch_trapdoor[facing=north,half=bottom,open=true]")
c.box(3, 5, 19, 5, 5, 21, "smooth_stone_slab")
# 風速計
c.box(10, 1, 20, 10, 6, 20, "spruce_fence")
c.set(10, 7, 20, "lightning_rod[facing=up]")
for (dx, dz) in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
    c.set(10 + dx, 6, 20 + dz, "cobblestone_wall")
# 天線塔
c.box(26, 1, 18, 26, 22, 18, "iron_bars")
for y in (6, 12, 18):
    c.set(26, y, 18, "red_concrete")
c.set(26, 23, 18, "redstone_lamp[lit=true]")
# 油槽
for z0 in (13, 16):
    c.box(23, 1, z0, 28, 2, z0 + 1, "iron_block")
    c.box(23, 1, z0, 23, 2, z0 + 1, "light_gray_concrete")
    c.box(28, 1, z0, 28, 2, z0 + 1, "light_gray_concrete")
    c.set(24, 1, z0 - 1 if z0 == 13 else z0 + 2, "lever[face=floor,facing=north]")
# 破損圍欄
for x in range(-5, 34):
    for z in (-5, 25):
        if c.chance(0.72):
            c.set(x, 1, z, "spruce_fence[east=true,west=true]")
for z in range(-5, 26):
    for x in (-5, 33):
        if c.chance(0.72):
            c.set(x, 1, z, "spruce_fence[north=true,south=true]")
# 院子積雪與迎風面雪堆（北側、西側）
for x in range(-7, 37):
    for z in range(-7, 28):
        if (x, 1, z) in c.blocks:
            continue
        inside = MAIN[0] <= x <= MAIN[1] and MAIN[2] <= z <= MAIN[3] or ANNEX[0] <= x <= ANNEX[1] and ANNEX[2] <= z <= ANNEX[3]
        if inside:
            continue
        near_north = z in (-1, -2) and -1 <= x <= 30
        near_west = x in (-1, -2) and -1 <= z <= 16
        if (near_north or near_west) and c.chance(0.8):
            c.set(x, 1, z, "snow_block" if c.chance(0.4) else f"snow[layers={c.rng.randint(4, 7)}]")
        elif c.chance(0.55):
            c.set(x, 1, z, f"snow[layers={c.rng.randint(1, 3)}]")

# 告示牌
c.post.append(
    "setblock ~30 ~3 ~2 spruce_wall_sign[facing=east]"
    "{front_text:{messages:['{\"text\":\"МЕТЕОСТАНЦИЯ\"}','{\"text\":\"№ 7\"}','{\"text\":\"高山氣象站 7 號\"}','{\"text\":\"\"}']}}"
)

# ---------------------------------------------------------------- 輸出
out_fn = ROOT / "datapack/longnight/data/ln/functions/build/weather_station.mcfunction"
n = c.write(out_fn, "# 由 generators/weather_station.py 自動產生，請勿手動修改")


def a(x, y, z):
    return [ORIGIN[0] + x, ORIGIN[1] + y, ORIGIN[2] + z]


anchors = {
    "origin": list(ORIGIN),
    "garage_door_outside": a(32, 1, 5),     # 進站觸發點
    "player_inside": a(25, 1, 7),
    "fox_bench": a(6, 1, 5),
    "tank_radio": a(4, 1, 6),
    "officer_radio": a(3, 1, 3),
    "baiya_tower": a(3, 6, 3),
    "parts_button": a(27, 2, 9),
    "checkpoint": a(12, 1, 8),
    "boiler": a(15, 1, 3),
    "start_center": [172, 960],             # 山下起點（x, z），高度在執行時自動貼地
    "enemy_spawns": {                       # 敵人出現的中心（x, z）
        "east": [ORIGIN[0] + 62, ORIGIN[2] + 6],
        "north": [ORIGIN[0] + 12, ORIGIN[2] - 34],
        "south": [ORIGIN[0] + 14, ORIGIN[2] + 46],
        "west": [ORIGIN[0] - 30, ORIGIN[2] + 8],
    },
}
(ROOT / "generators/out").mkdir(exist_ok=True)
(ROOT / "generators/out/weather_station.json").write_text(json.dumps(anchors, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"weather_station.mcfunction：{n} 行指令；原點 {ORIGIN}")
