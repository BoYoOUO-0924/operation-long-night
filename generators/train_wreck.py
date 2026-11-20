"""第五章開場：裝甲列車翻覆現場（第四章結尾的後果）。

配置（絕對座標，鐵路沿山谷南北走向，路堤頂 y=108）：
  - 北段（z 938～952）：鐵軌被炸斷，彈坑、扭曲的鐵軌、焦黑地面
  - 車頭（z 952～966）：衝出軌道，側翻倒在路堤東側的雪溝裡，起火冒煙
  - 運兵車廂（z 960～974）：出軌、往西傾斜，車頭端插進雪堆；西側有一扇鐵門（戰車踹開的那扇）
  - 後段車廂（z 978～992）：還在軌道上，但車輪脫軌、歪斜
小隊從運兵車廂西側的門爬出來，往西爬坡就是開場位置，再往西上山就是氣象站。

執行：python generators/train_wreck.py → datapack/.../build/train_wreck.mcfunction 與 generators/out/train_wreck.json
"""
import json
from pathlib import Path

from canvas import Canvas

ROOT = Path(__file__).resolve().parent.parent
HM = json.loads((ROOT / "generators/out/heightmap_ch05.json").read_text(encoding="utf-8"))
O = (185, 100, 925)               # 原點（絕對座標）；畫布裡都用絕對座標，輸出時再扣掉
BED = 108                         # 路堤頂面
RAIL_X = 203

c = Canvas(seed=11)
rng = c.rng


def S(x, y, z, b):
    c.blocks[(x - O[0], y - O[1], z - O[2])] = b


def G(x, z):
    """絕對座標的地表高度（超出高度圖就當 104）"""
    if HM["x1"] <= x <= HM["x2"] and HM["z1"] <= z <= HM["z2"]:
        return HM["top"][z - HM["z1"]][x - HM["x1"]]
    return 104


def box(x1, y1, z1, x2, y2, z2, b):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            for z in range(min(z1, z2), max(z1, z2) + 1):
                S(x, y, z, b() if callable(b) else b)


olive = c.pick([("green_terracotta", 86), ("brown_terracotta", 6), ("gray_terracotta", 8)])
dark = c.pick([("gray_concrete", 50), ("black_concrete", 30), ("polished_blackstone", 20)])
plate = c.pick([("gray_concrete", 70), ("iron_block", 20), ("polished_andesite", 10)])
burnt = c.pick([("blackstone", 35), ("coal_block", 20), ("gravel", 20), ("black_concrete_powder", 20), ("magma_block", 5)])
gravel = c.pick([("gravel", 60), ("andesite", 25), ("cobblestone", 15)])

# ================================================================ 路堤與鐵軌（z 926～999）
for z in range(926, 1000):
    for x in range(200, 208):
        g = G(x, z)
        edge = x in (200, 207)
        top = BED - (1 if edge else 0)
        for y in range(min(g, top) - 2, top + 1):
            S(x, y, z, gravel() if y == top else "stone")
        for y in range(top + 1, max(g, top) + 4):
            S(x, y, z, "air")
        if edge and rng.random() < 0.6:
            S(x, top + 1, z, f"snow[layers={rng.randint(1, 3)}]")
    if not (938 <= z <= 952):                                  # 炸斷的那段沒有鐵軌
        S(RAIL_X, BED + 1, z, "rail[shape=north_south]")
        S(RAIL_X + 2, BED + 1, z, "rail[shape=north_south]")   # 雙線（第二條給後段車廂）

# ================================================================ 運兵車廂西側的雪溝（原本是山坡，挖出來讓門外有地方站、往西是爬坡）
for z in range(955, 980):
    for x in range(186, 200):
        g = G(x, z)
        floor = BED - 1 + max(0, 195 - x) + (1 if z in (955, 979) else 0)
        if floor >= g:
            continue
        for y in range(floor + 1, g + 3):
            S(x, y, z, "air")
        S(x, floor, z, "snow_block")
        if rng.random() < 0.5:
            S(x, floor + 1, z, f"snow[layers={rng.randint(1, 4)}]")

# ================================================================ 炸斷的鐵軌與彈坑（z 938～952）
cx, cz = 204, 945
for x in range(197, 212):
    for z in range(936, 955):
        d = ((x - cx) ** 2 + (z - cz) ** 2) ** 0.5
        if d < 7:
            depth = int(3 * (1 - d / 7)) + 1
            for y in range(BED - depth + 1, BED + 3):
                S(x, y, z, "air")
            S(x, BED - depth, z, burnt())
            if rng.random() < 0.04:
                S(x, BED - depth + 1, z, "fire")
        elif d < 10 and rng.random() < 0.5:                    # 外圈焦黑、碎石
            S(x, G(x, z) if G(x, z) <= BED else BED, z, burnt())
# 扭曲翹起的鐵軌（斷口往上翻）
for (x, z, h) in [(203, 937, 3), (205, 937, 2), (203, 953, 2), (205, 953, 4)]:
    for i in range(h):
        S(x + (i // 2 if x == 205 else -(i // 2)), BED + 1 + i, z + (1 if z < 945 else -1) * (i // 2), "iron_bars")
    S(x, BED + 1, z, "rail[shape=north_south]")
for (x, y, z) in [(201, BED + 1, 941), (208, BED, 948), (206, BED - 1, 943), (199, BED, 950)]:
    S(x, y, z, rng.choice(["chain[axis=x]", "iron_bars", "anvil[facing=north]", "lightning_rod[facing=east]"]))


# ================================================================ 車廂（直立，可以往西傾斜、車頭端下沉）
def car(x1, z1, length, y0, lean=0.0, nose=0, door_z=None, locomotive=False):
    """x1 = 西側牆、車寬 5；z1 = 北端；lean = 每升高一格往西偏幾格；nose = 北端下沉幾格（漸變到中段）"""
    w, h = 5, 5
    for dz in range(length):
        z = z1 + dz
        drop = round(nose * max(0, 1 - dz / (length * 0.6)))
        for dy in range(-1, h + 1):
            y = y0 + dy - drop
            shift = -int(dy * lean)
            for dx in range(w):
                x = x1 + dx + shift
                wall = dx in (0, w - 1) or dz in (0, length - 1)
                if dy == -1:                                   # 底盤與轉向架
                    b = "black_concrete" if dx in (1, 3) and dz % 6 in (1, 2) else ("polished_blackstone" if dx in (0, 4) else "air")
                elif dy == 0:
                    b = dark()
                elif dy == h:
                    b = plate() if dx in (0, w - 1) or dz in (0, length - 1) else "gray_concrete"
                elif wall:
                    b = "iron_block" if dy == 2 and rng.random() < 0.7 else olive()
                    if dy == 3 and dx in (0, w - 1) and dz % 4 == 2:
                        b = "iron_bars"                        # 射擊孔
                else:
                    b = "air"
                if b != "air" or not wall:
                    S(x, y, z, b)
        if rng.random() < 0.3:                                 # 車頂積雪
            S(x1 + rng.randint(0, w - 1) - int(h * lean), y0 + h + 1 - drop, z, f"snow[layers={rng.randint(1, 4)}]")
    if door_z is not None:                                     # 西側鐵門（關著，劇情用指令踹開）
        dy = 1
        x = x1 - int(dy * lean)
        y = y0 + dy - round(nose * max(0, 1 - (door_z - z1) / (length * 0.6)))
        S(x, y, door_z, "iron_door[facing=west,half=lower,hinge=left,open=false]")
        S(x, y + 1, door_z, "iron_door[facing=west,half=upper,hinge=left,open=false]")
        return (x, y, door_z)
    return None


def scorch(x1, y1, z1, x2, y2, z2, p):
    for (x, y, z), b in list(c.blocks.items()):
        ax, ay, az = x + O[0], y + O[1], z + O[2]
        if x1 <= ax <= x2 and y1 <= ay <= y2 and z1 <= az <= z2 and b not in ("air",) and "snow" not in b and "door" not in b:
            if rng.random() < p:
                c.blocks[(x, y, z)] = burnt() if rng.random() < 0.8 else "air"


# 運兵車廂：出軌往西傾斜，北端插進雪堆
DOOR = car(197, 960, 15, BED, lean=0.25, nose=2, door_z=968)
# 雪堆把北端埋住
for x in range(193, 204):
    for z in range(955, 963):
        top = BED + 1 + (962 - z) // 3 - abs(x - 198) // 3 + rng.choice([0, 0, 1, -1])
        for y in range(BED - 1, top):
            if c.blocks.get((x - O[0], y - O[1], z - O[2])) in (None, "air"):
                S(x, y, z, "snow_block")
# 後段車廂：還在軌道上但歪斜
car(204, 978, 14, BED + 1, lean=0.0)
scorch(203, BED, 978, 210, BED + 7, 982, 0.25)

# 車頭：側翻倒在路堤東側（長 14、原本的「上方」朝東）
LZ1, LZ2 = 952, 966
lx = 207
ly = G(209, 958) - 1
for z in range(LZ1, LZ2 + 1):
    for dx in range(6):             # 原本的高度（底 → 頂）變成往東
        for dy in range(5):         # 原本的寬度變成高度
            x, y = lx + dx, ly + dy
            shell = dy in (0, 4) or dx in (0, 5) or z in (LZ1, LZ2)
            if not shell:
                S(x, y, z, "air")
                continue
            if dx == 0:             # 朝天的車底：輪子
                b = "black_concrete" if (z - LZ1) % 4 in (1, 2) and dy in (1, 3) else "polished_blackstone"
            elif dx == 5:
                b = plate()
            else:
                b = olive() if rng.random() < 0.8 else "iron_block"
            S(x, y, z, b)
    if (z - LZ1) % 5 == 2:
        S(lx + 3, ly + 4, z, "iron_bars")                      # 側窗（現在朝上）
box(lx + 1, ly + 5, LZ1 + 1, lx + 4, ly + 5, LZ1 + 3, "coal_block")   # 車頭前段炸開焦黑
scorch(lx, ly, LZ1, lx + 6, ly + 6, LZ1 + 6, 0.35)
# 雪溝：車頭一半埋在雪裡
for z in range(LZ1 - 1, LZ2 + 2):
    for x in range(lx - 1, lx + 8):
        if c.blocks.get((x - O[0], ly - O[1], z - O[2])) is None:
            for y in range(G(x, z), ly + 2):
                S(x, y, z, "snow_block")

# ================================================================ 火與煙（營火藏在殘骸裡冒煙；乾草塊讓煙柱更高）
FIRES = [(lx + 2, ly + 5, LZ1 + 2), (lx + 3, ly + 5, LZ1 + 9), (200, BED + 4, 962), (206, BED + 7, 980), (204, BED - 1, 945)]
for (x, y, z) in FIRES:
    S(x, y - 1, z, "hay_block")
    S(x, y, z, "campfire[lit=true,signal_fire=true]")
for (x, y, z) in [(lx + 1, ly + 5, LZ1 + 5), (lx + 4, ly + 5, LZ1 + 1), (201, BED + 3, 961), (205, BED + 7, 984)]:
    S(x, y - 1, z, "netherrack")
    S(x, y, z, "fire")

# 散落的物資與碎片
for (x, z) in [(198, 976), (195, 970), (209, 970), (200, 955), (196, 958), (210, 988)]:
    y = max(G(x, z), BED - 1 if 200 <= x <= 207 else 0) + 1
    S(x, y, z, rng.choice(["barrel[facing=up]", "iron_block", "anvil[facing=east]", "polished_blackstone_slab", "chest[facing=west]"]))

# ================================================================ 把整片山谷蓋上雪（原本是草地）：草地、泥土換成雪塊，花草清掉，生態域改成雪坡
SX1, SX2, SZ1, SZ2 = 160, 235, 912, 1010
for bx in range(SX1, SX2 + 1, 16):            # fillbiome 一次最多 32768 格，分塊執行
    for bz in range(SZ1, SZ2 + 1, 16):
        c.pre.insert(0, f"fillbiome ~{bx - O[0]} ~{60 - O[1]} ~{bz - O[2]} ~{min(bx + 15, SX2) - O[0]} ~{170 - O[1]} ~{min(bz + 15, SZ2) - O[2]} minecraft:snowy_slopes")
for y in range(85, 131):
    for (z1, z2) in [(SZ1, 960), (961, SZ2)]:
        r = f"~{SX1 - O[0]} ~{y - O[1]} ~{z1 - O[2]} ~{SX2 - O[0]} ~{y - O[1]} ~{z2 - O[2]}"
        c.pre.append(f"fill {r} snow_block replace grass_block")
        c.pre.append(f"fill {r} snow_block replace podzol")
        for plant in ("grass", "tall_grass", "fern", "large_fern", "#minecraft:small_flowers", "sweet_berry_bush"):
            c.pre.append(f"fill {r} air replace {plant}")

# ================================================================ 輸出
out = ROOT / "datapack/longnight/data/ln/functions/build/train_wreck.mcfunction"
c.pre.append("# 先清掉殘骸範圍裡原本的雪層，避免懸空")
n = c.write(out, "# 由 generators/train_wreck.py 自動產生，請勿手動修改\n"
                 f"# 執行：execute positioned {O[0]} {O[1]} {O[2]} run function ln:build/train_wreck")
anchors = {
    "origin": list(O),
    "door": list(DOOR),                                          # 運兵車廂西側鐵門（下半）
    "door_outside": [DOOR[0] - 2, DOOR[1], DOOR[2]],
    "squad_climb": [188, G(188, 966) + 1, 966],                 # 爬出來後往西走到的位置
    "rail_break": [204, BED + 1, 936],
    "loco": [lx + 3, ly + 3, (LZ1 + LZ2) // 2],
    "car_center": [199, BED + 3, 967],
    "fires": [list(f) for f in FIRES],
}
(ROOT / "generators/out/train_wreck.json").write_text(json.dumps(anchors, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"train_wreck.mcfunction：{n} 行指令；門 {DOOR}")
