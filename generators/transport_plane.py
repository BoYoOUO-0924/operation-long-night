"""遊戲大廳：萬米高空巡航中的戰術運輸機貨艙（參考 C-17，機艙放大到 15 格寬）。

局部座標：x 往東（機身中心線 x=8，機艙內部 x=1..15），z 往南（機頭 z=0 → 機尾 z=52），
y=0 是貨艙地板方塊，空氣從 y=1 開始。原點 = 機身西側、機頭的地板。
由機頭到機尾：
  z 0..7    駕駛艙（地板高 1 格）＋隔艙門
  z 9..13   全息作戰桌（章節選擇、準備就緒）
  z 15..27  左：機動軍械庫（槍架、改槍台、軍刀展示）；右：P1～P4 傘兵座椅＋背包架
  z 28..33  右：獵犬小隊（戰車、白鴉、狐狸）；中：貨物棧板
  z 39..44  機尾：跳傘燈、護欄
  z 45..52  跳板（平常只放下一半並有護欄；跳傘時完全放平、拆掉護欄）
執行：python generators/transport_plane.py
"""
import json
from pathlib import Path

from canvas import Canvas

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = (-310, 272, 900)          # 遠離第五章、比山頂和雲層（y≈192）都高
CX = 8                              # 機身中心線

c = Canvas(seed=11)

# ---------------------------------------------------------------- 截面
HOLD_HW = {1: 7, 2: 7, 3: 7, 4: 7, 5: 6, 6: 5, 7: 3}         # 貨艙每一層的半寬
COCK_HW = {2: 5, 3: 5, 4: 5, 5: 5, 6: 4, 7: 2}               # 駕駛艙（地板 y=1）
Z_COCK, Z_BULK, Z_TAIL = (1, 6), 7, 44


def interior(x, y, z):
    dx = abs(x - CX)
    if Z_COCK[0] <= z <= Z_COCK[1]:
        taper = {1: 2, 2: 1}.get(z, 0)                      # 機鼻收窄
        hw = COCK_HW.get(y)
        return hw is not None and dx <= hw - taper
    if Z_BULK < z <= Z_TAIL:
        hw = HOLD_HW.get(y)
        return hw is not None and dx <= hw
    return False


SKIN = c.pick([("light_gray_concrete", 8), ("smooth_stone", 1)])   # 不要用混凝土粉末：會受重力掉下來
cells = set()
for z in range(0, Z_TAIL + 1):
    for y in range(0, 10):
        for x in range(-1, 18):
            if interior(x, y, z):
                cells.add((x, y, z))
shell = set()
for (x, y, z) in cells:
    for ddx in (-1, 0, 1):
        for ddy in (-1, 0, 1):
            for ddz in (-1, 0, 1):
                n = (x + ddx, y + ddy, z + ddz)
                if n not in cells and n[2] <= Z_TAIL:
                    shell.add(n)
for (x, y, z) in shell:
    c.set(x, y, z, SKIN() if y > 0 else "gray_concrete")
for (x, y, z) in cells:
    c.set(x, y, z, "air")

# 隔艙牆（駕駛艙 ↔ 貨艙），門 x7..9
for y in range(1, 8):
    for x in range(1, 16):
        if interior(x, y, Z_BULK + 1):
            c.set(x, y, Z_BULK, "gray_concrete")
c.box(7, 2, Z_BULK, 9, 4, Z_BULK, "air")
c.box(7, 1, Z_BULK, 9, 1, Z_BULK, "polished_deepslate")
for x in (7, 8, 9):
    c.set(x, 1, Z_BULK + 1, "polished_deepslate_stairs[facing=north]")   # 上駕駛艙的台階
c.set(6, 2, Z_BULK, "iron_bars"); c.set(10, 2, Z_BULK, "iron_bars")

# ---------------------------------------------------------------- 地板與骨架
for z in range(Z_BULK + 1, Z_TAIL + 1):
    for x in range(1, 16):
        c.set(x, 0, z, "polished_andesite" if x not in (4, 12) else "polished_deepslate")   # 兩條貨物滾輪軌
    if z % 4 == 0:                                                # 機身肋骨
        for (x, y, zz) in shell:
            if zz == z and y > 0:
                c.set(x, y, zz, "gray_concrete")
# 天花板燈（之後跳傘時整排換成紅燈）
CEIL_LIGHTS = []
for z in range(10, Z_TAIL, 4):
    c.set(CX, 8, z, "sea_lantern")
    CEIL_LIGHTS.append((CX, 8, z))
# 兩側線槽
for z in range(Z_BULK + 1, Z_TAIL + 1):
    c.set(2, 6, z, "iron_bars") if interior(2, 6, z) else None
    c.set(14, 6, z, "iron_bars") if interior(14, 6, z) else None

# ---------------------------------------------------------------- 1. 駕駛艙
for x in range(3, 14):
    for z in range(1, Z_BULK):
        if interior(x, 2, z):
            c.set(x, 1, z, "polished_blackstone")
for z in (0, 1, 2):                                               # 擋風玻璃
    for y in (4, 5, 6):
        for x in range(2, 15):
            if (x, y, z) in shell and z <= 2:
                c.set(x, y, z, "black_stained_glass")             # 抗眩光座艙罩：黑色染色玻璃，沒有白色網格線
for z in (3, 4):                                                  # 側窗
    for y in (4, 5):
        c.set(2, y, z, "black_stained_glass"); c.set(14, y, z, "black_stained_glass")
# 傾斜儀表控台：深板岩底座＋往飛行員方向傾斜的深板岩階梯，上面放拉桿與按鈕，正面掛發光展示框（時鐘／羅盤／地圖）
c.box(4, 2, 2, 12, 2, 2, "polished_deepslate")
c.box(4, 3, 2, 12, 3, 2, "polished_deepslate_stairs[facing=north,half=bottom]")
for x in (4, 12):
    c.set(x, 4, 2, "polished_blackstone_button[face=floor,facing=south]")
for x in (6, 10):
    c.set(x, 4, 2, "lever[face=floor,facing=south]")
for x in (7, 9):
    c.set(x, 4, 2, "stone_button[face=floor,facing=south]")
c.set(8, 2, 3, "polished_deepslate_wall")                         # 中央油門台
c.set(8, 3, 3, "lightning_rod[facing=up]")
DASH_FRAMES = [(5, 3, 3, "clock"), (7, 3, 3, "compass"), (9, 3, 3, "map"), (11, 3, 3, "clock")]
# 頭頂開關面板：天花板下的鐵活板門＋往下垂的終界燭
for x in range(6, 11):
    for z in (3, 4, 5):
        if interior(x, 7, z):
            c.set(x, 7, z, "iron_trapdoor[half=top,facing=south,open=false]")
for (x, z) in ((7, 4), (9, 4), (8, 5)):
    c.set(x, 6, z, "end_rod[facing=down]")
PILOT_SEATS = [(6, 2, 4), (10, 2, 4)]
for (x, y, z) in PILOT_SEATS:
    c.set(x, y, z, "blackstone_stairs[facing=south]")

# ---------------------------------------------------------------- 2. 全息作戰桌
TABLE = (5, 11, 10, 12)        # x1, x2, z1, z2
for x in range(TABLE[0], TABLE[1] + 1):
    for z in range(TABLE[2], TABLE[3] + 1):
        edge = x in (TABLE[0], TABLE[1]) or z in (TABLE[2], TABLE[3])
        c.set(x, 1, z, "polished_blackstone" if edge else "light_blue_stained_glass")
        if not edge:
            c.set(x, 0, z, "sea_lantern")
# 微縮地形（全息）：之後依選到的章節換，現在先放第一章海岸的抽象形狀
HOLO = [(7, 2, 11, "light_blue_stained_glass"), (8, 2, 11, "light_blue_stained_glass"), (9, 2, 11, "cyan_stained_glass")]

# ---------------------------------------------------------------- 3. 機動軍械庫（左側 x=1..3）
for z in range(15, 28):                                            # 掛槍牆：深板岩底板＋鐵柵欄網格
    for y in (2, 3, 4):
        c.set(0, y, z, "polished_deepslate"); c.set(1, y, z, "iron_bars")
for z in range(15, 28, 3):                                         # 暖琥珀工作燈
    c.set(2, 5, z, "ochre_froglight")
for z in (17, 23):                                                 # 座椅區的冷色頂燈
    c.set(14, 5, z, "sea_lantern")
c.set(2, 1, 17, "tacz:gun_smith_table[facing=east]")
c.box(2, 1, 20, 2, 1, 23, "iron_trapdoor[half=top,facing=east,open=false]")      # 折疊工作台（金屬）
ATT_BARRELS = [(2, 1, 24), (2, 1, 25), (2, 1, 26)]                  # 無限配件補給箱（瞄具／槍口握把／彈匣槍托），內容由 build_lobby.py 補滿
for (x, y, z) in ATT_BARRELS:
    c.set(x, y, z, "barrel[facing=east]")
# 一鍵兵種終端機（軍械庫尾端）：按鈕由 build_lobby.py 放
c.box(2, 1, 28, 3, 1, 28, "polished_deepslate")
c.box(2, 2, 28, 3, 2, 28, "iron_trapdoor[half=bottom,facing=east,open=false]")

# ---------------------------------------------------------------- 4. P1～P4 傘兵座椅（右側 x=13..15）
SEATS = []
for i, z in enumerate((16, 19, 22, 25)):
    c.set(14, 1, z, "crimson_stairs[facing=east]")
    c.set(15, 2, z, "red_concrete"); c.set(15, 3, z, "black_concrete")
    c.set(15, 1, z - 1, "black_concrete"); c.set(15, 1, z + 1, "black_concrete")
    c.set(15, 4, z, "barrel[facing=west]")                         # 背包架（第二階段：戰術套件）
    c.set(14, 5, z, "iron_trapdoor[half=top,facing=west,open=false]")
    SEATS.append((14, 1, z))

# ---------------------------------------------------------------- 獵犬小隊區（右側 z=28..33）＋ 中央貨物
c.set(13, 1, 29, "barrel[facing=up]"); c.set(13, 1, 30, "barrel[facing=up]")   # 戰車坐的彈藥箱
c.set(12, 1, 29, "spruce_planks")
c.set(14, 1, 33, "black_shulker_box[facing=up]")                  # 狐狸的通訊箱
c.set(14, 2, 33, "daylight_detector[inverted=true]")
c.box(2, 1, 30, 5, 1, 36, "spruce_slab[type=bottom]")           # 貨物棧板（靠左，不擋往機尾的視線）
c.box(2, 2, 30, 3, 3, 32, "spruce_planks"); c.box(4, 2, 33, 5, 2, 36, "barrel[facing=up]")
c.box(2, 2, 34, 3, 2, 36, "green_terracotta")
for z in (30, 36):
    c.set(4, 2, z, "chain[axis=x]")

# ---------------------------------------------------------------- 戰術物資箱（取代突兀的單顆方塊）
CRATES = [  # 位置, 種類
    ((3, 1, 10), "gray_shulker_box[facing=up]"), ((3, 2, 10), "green_shulker_box[facing=up]"),
    ((3, 1, 11), "black_shulker_box[facing=up]"),
    ((13, 1, 10), "green_shulker_box[facing=up]"), ((13, 1, 12), "gray_shulker_box[facing=up]"),
    ((3, 2, 6), "black_shulker_box[facing=up]"), ((13, 2, 6), "gray_shulker_box[facing=up]"),
    ((3, 1, 15), "green_shulker_box[facing=up]"), ((3, 1, 27), "gray_shulker_box[facing=up]"),
    ((14, 1, 27), "gray_shulker_box[facing=up]"), ((14, 2, 27), "black_shulker_box[facing=up]"),
]
for (pos, b) in CRATES:
    c.set(*pos, b)
# 鐵活板門包覆的物資箱（綠色箱體四面貼鐵板）
for (x, z) in ((12, 14), (4, 38)):
    c.set(x, 1, z, "green_terracotta")
    c.set(x, 2, z, "iron_trapdoor[half=bottom,facing=north,open=false]")
    c.set(x + 1, 1, z, "iron_trapdoor[facing=east,open=true]"); c.set(x - 1, 1, z, "iron_trapdoor[facing=west,open=true]")
    c.set(x, 1, z - 1, "iron_trapdoor[facing=north,open=true]"); c.set(x, 1, z + 1, "iron_trapdoor[facing=south,open=true]")
# 戰術彈藥箱：深色橡木階梯（倒放）＋告示牌標示口徑
AMMO = [((13, 1, 11), "west", "5.56 NATO"), ((3, 1, 19), "east", "7.62x39"), ((14, 1, 13), "west", "12 GA")]
for ((x, y, z), face, label) in AMMO:
    c.set(x, y, z, f"dark_oak_stairs[facing={face},half=top]")
    sx = x - 1 if face == "west" else x + 1
    c.set(sx, y, z, f"dark_oak_wall_sign[facing={face}]")
    c.post.append("data merge block ~%d ~%d ~%d {front_text:{color:\"white\",has_glowing_text:1b,messages:['\"\"','{\"text\":\"%s\"}','{\"text\":\"AMMO\"}','\"\"']}}" % (sx, y, z, label))

# ---------------------------------------------------------------- 機尾、跳板
c.set(1, 4, 42, "redstone_lamp[lit=false]"); c.set(1, 4, 43, "lime_concrete")   # 跳傘燈（紅：準備／綠：跳）
c.set(15, 4, 42, "redstone_lamp[lit=false]"); c.set(15, 4, 43, "lime_concrete")
for x in range(1, 16):
    c.set(x, 0, 45, "polished_andesite"); c.set(x, 0, 46, "polished_andesite")
    c.set(x, 0, 47, "polished_andesite"); c.set(x, 0, 48, "polished_andesite")
for z in range(45, 49):
    c.set(0, 0, z, "gray_concrete"); c.set(16, 0, z, "gray_concrete")
    c.set(1, 1, z, "iron_bars"); c.set(15, 1, z, "iron_bars")   # 跳板兩側護欄
RAIL_Z = 46
for x in range(2, 15):
    c.set(x, 1, RAIL_Z, "iron_bars")                              # 安全護欄（跳傘時拆掉）

# ---------------------------------------------------------------- 外觀：上單翼、四具發動機、T 型尾翼
# 機鼻：從駕駛艙前牆往前延伸 7 格，截面橢圓逐漸收窄；上半平滑石英、下半灰色混凝土，最前端深色雷達罩
NOSE = [(4.4, 2.7), (4.1, 2.5), (3.6, 2.2), (3.0, 1.9), (2.3, 1.5), (1.6, 1.1), (0.9, 0.7)]
for k, (rx, ry) in enumerate(NOSE, start=1):
    z = -k
    cy = 2.3 - k * 0.12                                            # 機鼻略往下垂
    cells_k = [(x, y) for x in range(0, 17) for y in range(0, 6)
               if ((x - CX) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0]
    top = {}
    for (x, y) in cells_k:
        top[x] = max(top.get(x, -1), y)
    for (x, y) in cells_k:
        if k >= 6:
            b = "blackstone" if (x + y) % 2 else "polished_blackstone"      # 雷達罩（撞色）
        elif y >= cy:
            b = "smooth_quartz"
        else:
            b = "gray_concrete"
        if y == top[x] and k <= 5 and y >= cy and abs(x - CX) >= 1:
            b = "smooth_quartz_slab[type=bottom]"                  # 頂部邊緣用半磚削出錐度
        c.set(x, y, z, b)


def fuselage(x, y, z):
    return interior(x, y, z) or (x, y, z) in shell


# 主翼：上單翼，翼根加寬（z 12..28）、往翼尖收窄並後掠
for x in range(-24, 41):
    d = max(0, abs(x - CX) - 4)                                     # 離機背邊緣的距離
    if d > 27:
        continue
    le = 12 + d * 0.42
    te = 28 - d * 0.16
    for z in range(int(le), int(te) + 1):
        if not fuselage(x, 8, z):
            c.set(x, 8, z, "light_gray_concrete")
        if d <= 7 and not fuselage(x, 7, z) and z <= te - 1:
            c.set(x, 7, z, "gray_concrete")                         # 翼根加厚
# 四具大型渦輪發動機短艙：用深板岩牆＋鐵砧吊在機翼下方
NACELLES = []
for d in (9, 18):
    for x0 in (4 - d, 12 + d):
        le = int(12 + d * 0.42)
        z1, z2 = le - 5, le + 5
        for z in range(z1, z2 + 1):
            r = 2.2 if z1 < z < z2 else 1.6
            for x in range(x0 - 2, x0 + 3):
                for y in range(2, 7):
                    if (x - x0) ** 2 + (y - 4.5) ** 2 <= r * r:
                        if z == z1:
                            b = "black_concrete" if (x - x0) ** 2 + (y - 4.5) ** 2 <= 1.3 else "gray_concrete"
                        elif z == z2:
                            b = "polished_blackstone"
                        else:
                            b = "light_gray_concrete" if y >= 5 else "gray_concrete"
                        c.set(x, y, z, b)
        for z in range(le - 1, le + 4):
            c.set(x0, 7, z, "polished_deepslate_wall")                # 吊架
        c.set(x0, 7, le + 1, "anvil[facing=north]")
        NACELLES.append((x0, z1, z2))
# 翼尖航行燈：左紅右綠，發光方塊外面包染色玻璃
for (tx, core, glass) in ((CX - 4 - 28, "shroomlight", "red_stained_glass"), (CX + 4 + 28, "verdant_froglight", "lime_stained_glass")):
    tz = int(12 + 27 * 0.42) + 1
    c.set(tx, 8, tz, core)
    for (ddx, ddy, ddz) in ((-1, 0, 0), (1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, -1), (0, 0, 1)):
        c.set(tx + ddx, 8 + ddy, tz + ddz, glass)
for z in range(36, 47):
    h = 9 + (z - 36)
    c.box(CX, 9, z, CX, min(h, 20), z, "light_gray_concrete")      # 垂直尾翼
c.box(CX - 9, 20, 42, CX + 9, 20, 47, "light_gray_concrete")       # 水平尾翼

# ---------------------------------------------------------------- 實體裝飾（建造時一起放）
c.pre += [f"fill ~-26 ~-2 ~{z0} ~42 ~22 ~{z0 + 17} air" for z0 in (-9, 9, 27, 45)]
c.pre.append("kill @e[tag=ln_lobby_deco]")
for i, (x, y, z) in enumerate(SEATS):
    col = ["#7FC8E8", "#8EE07A", "#F0A040", "#C08CF0"][i]
    c.post.append(
        f'summon text_display ~{x + 0.45} ~{y + 2.25} ~{z + 0.5} {{Tags:["ln_lobby_deco"],billboard:"fixed",'
        f"transformation:{{left_rotation:[0f,0.7071f,0f,-0.7071f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[1.2f,1.2f,1.2f]}},"
        f"background:0,text:'{{\"text\":\"P{i + 1}\",\"color\":\"{col}\",\"font\":\"lnai:ui\"}}'}}")
c.post.append(
    'summon text_display ~2.05 ~4.6 ~21 {Tags:["ln_lobby_deco"],billboard:"fixed",'
    "transformation:{left_rotation:[0f,0.7071f,0f,0.7071f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[1f,1f,1f]},"
    "background:0,text:'{\"text\":\"軍械庫  ARMORY\",\"color\":\"#F0A040\",\"font\":\"lnai:ui\"}'}")
for (x, y, z, item) in DASH_FRAMES:
    c.post.append(f'summon glow_item_frame ~{x} ~{y} ~{z} {{Tags:["ln_lobby_deco"],Facing:3b,Fixed:1b,Invisible:0b,Item:{{id:"minecraft:{item}",Count:1b}}}}')
# 補光（看不見的光源）：讓貨艙不要太暗
for z in range(10, Z_TAIL, 4):
    for x in (3, 13):
        c.set(x, 6, z, "light[level=11]") if interior(x, 6, z) else None

# ---------------------------------------------------------------- 傘兵靜力繩：座椅上方一條縱向鍊條，每個座位垂一段鍊子、旁邊掛鉤
for z in range(15, 28):
    c.set(13, 6, z, "chain[axis=z]")
for (x, y, z) in SEATS:
    c.set(13, 5, z, "chain[axis=y]")
    c.set(14, 4, z, "tripwire_hook[facing=west,attached=false]")


def free(x, y, z):
    return c.get(x, y, z) in (None, "air")


# 地板中線：兩排貨物滾輪軌
for z in range(14, Z_TAIL):
    for x in (7, 9):
        if free(x, 1, z):
            c.set(x, 1, z, "rail[shape=north_south]")
# 跳板邊緣黃黑警示線
for x in range(1, 16):
    c.set(x, 0, Z_TAIL, "yellow_concrete" if x % 2 else "black_concrete")
# C 型結構肋骨：每 3 格一圈，下段深板岩牆、上段石階梯（原版沒有平滑石階梯）＋平滑石半磚包住天花板
LIGHT_Z = {z for (_, _, z) in CEIL_LIGHTS}
for z in range(9, Z_TAIL, 3):
    for y in range(1, 8):
        for x in range(1, 16):
            if not interior(x, y, z) or not free(x, y, z):
                continue
            west, east = not interior(x - 1, y, z), not interior(x + 1, y, z)
            top = not interior(x, y + 1, z)
            if y <= 4:
                if west or east:
                    c.set(x, y, z, "polished_deepslate_wall")
            elif west or east:
                c.set(x, y, z, f"stone_stairs[facing={'west' if west else 'east'},half=top]")
            elif top and not (x == CX and z in LIGHT_Z):
                c.set(x, y, z, "smooth_stone_slab[type=top]")
# 天花板管線：兩條避雷針串起每一道肋骨
for z in range(Z_BULK + 1, Z_TAIL + 1):
    for x in (6, 10):
        if free(x, 7, z) and interior(x, 7, z):
            c.set(x, 7, z, "lightning_rod[facing=south]")

# ---------------------------------------------------------------- 輸出
out_fn = ROOT / "datapack/longnight/data/ln/functions/build/transport_plane.mcfunction"
n = c.write(out_fn, "# 由 generators/transport_plane.py 自動產生，請勿手動修改")


def a(x, y, z):
    return [ORIGIN[0] + x, ORIGIN[1] + y, ORIGIN[2] + z]


anchors = {
    "origin": list(ORIGIN),
    "box": [ORIGIN[0] - 26, ORIGIN[1] - 2, ORIGIN[2] - 9, ORIGIN[0] + 42, ORIGIN[1] + 22, ORIGIN[2] + 62],
    "floor_y": ORIGIN[1],
    "spawn": a(8, 1, 16),
    "table": a(8, 1, 11),
    "table_front_z": ORIGIN[2] + 13,
    "pilots": [a(x, y, z) for (x, y, z) in PILOT_SEATS],
    "seats": [a(x, y, z) for (x, y, z) in SEATS],
    "tank": a(13, 2, 29),
    "baiya": a(14, 1, 31),
    "fox": a(13, 1, 33),
    "ceil_lights": [a(*p) for p in CEIL_LIGHTS],
    "jump_lamps": [a(1, 4, 42), a(15, 4, 42)],
    "rail": [a(2, 1, RAIL_Z), a(14, 1, RAIL_Z)],
    "ramp_ext": [a(1, 0, 49), a(15, 0, 52)],
    "ramp_end_z": ORIGIN[2] + 52,
    "tail_z": ORIGIN[2] + Z_TAIL,
    "holo": [a(x, y, z) + [b] for (x, y, z, b) in HOLO],
    "att_barrels": [a(*b) for b in ATT_BARRELS],
}
(ROOT / "generators/out").mkdir(exist_ok=True)
(ROOT / "generators/out/transport_plane.json").write_text(json.dumps(anchors, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"transport_plane.mcfunction：{n} 行指令；原點 {ORIGIN}")
