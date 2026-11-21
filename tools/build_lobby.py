"""遊戲大廳（運輸機貨艙）的流程 → 資料包 functions/lobby/*。

第一階段：上線就在機艙、作戰桌選章節、全員「準備就緒」→ 紅光＋警報、跳板放平 → 綠燈跳下機尾 → 開始章節。
飛機本體由 generators/transport_plane.py 產生（錨點 generators/out/transport_plane.json）。
執行：python tools/build_lobby.py
"""
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P = json.loads((ROOT / "generators/out/transport_plane.json").read_text(encoding="utf-8"))
OUT = ROOT / "datapack/longnight/data/ln/functions/lobby"
O = P["origin"]
FY = P["floor_y"]
BX1, BY1, BZ1, BX2, BY2, BZ2 = P["box"]
FONT = "lnai:ui"

CHAPTERS = [  # 編號, 名稱, 地點, 開始函式（None = 製作中）
    (1, "雷霆空降", "海岸防空陣地・黑石海岸砲台", None),
    (2, "海岸線的葬禮", "懸崖觀測站", None),
    (3, "溺水之城", "半淹沒現代都市", None),
    (4, "鋼鐵狂飆", "峽谷裝甲列車", None),
    (5, "寒霜陷阱", "極寒山區氣象站", "ln:ch05/start"),
    (6, "深淵方舟", "地下核掩體", None),
    (7, "黎明前的最後防線", "衛星發射井核心", None),
    (8, "破曉", "海岸高地", None),
]
NUM = "一二三四五六七八"
GREEN_AT = 100          # 按下出發後幾 tick 轉綠燈（前面是紅燈倒數）
LAUNCH_TIMEOUT = 600    # 綠燈後最多等幾 tick 就自動出發（有人沒跳也一起走）

files = {}


def fn(name, lines):
    files[name] = lines


def jt(*parts):
    """組 JSON 文字（全部用戰術字型）"""
    out = []
    for p in parts:
        d = {"text": p} if isinstance(p, str) else dict(p)
        d.setdefault("font", FONT)
        out.append(d)
    return json.dumps(out if len(out) > 1 else out[0], ensure_ascii=False)


def sq(text_json):
    """放進 SNBT 單引號字串：反斜線要變兩個（\n 才會是換行），單引號要跳脫"""
    return text_json.replace("\\", "\\\\").replace("'", "\\'")


def xyz(p):
    return f"{p[0]} {p[1]} {p[2]}"


def in_lobby(extra=""):
    """選擇器：在飛機範圍內（含機艙下方 60 格，用來抓跳下去的人）"""
    return f"x={BX1},y={FY - 60},z={BZ1},dx={BX2 - BX1},dy={BY2 - FY + 60},dz={BZ2 - BZ1}{extra}"


SPAWN = P["spawn"]
TP_SPAWN = f"tp @s {SPAWN[0] + 0.5} {SPAWN[1]} {SPAWN[2] + 0.5} 180 0"
tx, ty, tz = P["table"]
TOP = ty + 1            # 桌面上緣

# ================================================================== 放置飛機與實體
place = [
    f"forceload add {BX1} {BZ1} {BX2} {BZ2}",
]
# 生物群系改成虛空：不會下雪下雨（分塊，fillbiome 一次最多 32768 格）
for z0 in range(BZ1, BZ2 + 1, 8):
    place.append(f"fillbiome {BX1} {BY1} {z0} {BX2} {BY2} {min(z0 + 7, BZ2)} minecraft:the_void")
place += [
    f"execute positioned {xyz(O)} run function ln:build/transport_plane",
    "kill @e[tag=ln_lobby]",
]
# 飛行員（坐姿，面向機頭）
for i, p in enumerate(P["pilots"]):
    place.append(
        f'summon tacznpcs:npc {p[0] + 0.5} {p[1] - 0.25} {p[2] + 0.5} {{template:"blue_support",templateInitialized:1b,'
        f'skin:{{texture:"tacznpcs:entity/villager1.png",slim:0b}},NoAI:1b,NoGravity:1b,Invulnerable:1b,Silent:1b,PersistenceRequired:1b,'
        f'Rotation:[180f,0f],Tags:["ln_lobby","lb_pilot"],HandItems:[{{}},{{}}],'
        f'ArmorItems:[{{id:"minecraft:leather_boots",Count:1b,tag:{{display:{{color:3355443}}}}}},{{id:"minecraft:leather_leggings",Count:1b,tag:{{display:{{color:4934475}}}}}},'
        f'{{id:"minecraft:leather_chestplate",Count:1b,tag:{{display:{{color:5592405}}}}}},{{id:"zerocontact:helmet_airframe",Count:1b}}]}}')
# 獵犬小隊（第二階段會加閒聊；現在先就定位）
SQUAD = [  # tag, 名字, 顏色, 模板, 位置, 面向, 動作, 頭盔, 防彈衣
    ("lb_tank", "戰車", "gold", "blue_support", P["tank"], 90, "sit_pilot", "helmet_bastion_black", "armor_6b43"),
    ("lb_baiya", "白鴉", "aqua", "blue_sniper", P["baiya"], 90, "guard", "helmet_tbh_iiia", "armor_jpc_v1"),
    ("lb_fox", "狐狸", "green", "blue_assault", P["fox"], -90, "wrist_tap", "helmet_phonetalker_iiia", "armor_avs"),
]
for tag, name, color, tpl, pos, yaw, _, _, _ in SQUAD:
    y = pos[1] - 0.25 if tag == "lb_tank" else pos[1]
    place.append(
        f'summon tacznpcs:npc {pos[0] + 0.5} {y} {pos[2] + 0.5} {{template:"{tpl}",'
        f"CustomName:'{json.dumps({'text': name, 'color': color}, ensure_ascii=False)}',"
        f'NoAI:1b,NoGravity:1b,Invulnerable:1b,PersistenceRequired:1b,Rotation:[{yaw}f,0f],Tags:["ln_lobby","lb_squad","{tag}"]}}')
place.append("schedule function ln:lobby/dress 3t replace")
fn("dress", [cmd for tag, *_r, helm, vest in SQUAD for cmd in (
    f"item replace entity @e[tag={tag}] armor.head with zerocontact:{helm}",
    f"item replace entity @e[tag={tag}] armor.chest with zerocontact:{vest}")] + ["function ln:lobby/anims"])
fn("anims", [f"lnhud anim @e[tag=lb_pilot] sit_pilot"] + [f"lnhud anim @e[tag={t}] {a}" for t, _n, _c, _t, _p, _y, a, *_ in SQUAD])

# 作戰桌：章節標題、狀態、按鈕（互動實體 + 文字）
fz = tz + 1.45          # 桌子南緣（玩家站的那一側）
place += [
    f"summon text_display {tx + 0.5} {TOP + 1.95} {tz + 0.5} {{Tags:[\"ln_lobby\",\"lb_title\"],billboard:\"vertical\",background:0,"
    f"transformation:{{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.8f,0.8f,0.8f]}},"
    f"text:'{jt({'text': '作戰簡報  MISSION BRIEFING', 'color': '#7FC8E8'})}'}}",
    f"summon text_display {tx + 0.5} {TOP + 1.0} {tz + 0.5} {{Tags:[\"ln_lobby\",\"lb_chap\"],billboard:\"vertical\",background:1711276032,"
    f"transformation:{{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[1.1f,1.1f,1.1f]}},text:'\"\"'}}",
    f"summon text_display {tx + 0.5} {TOP + 0.55} {tz + 0.5} {{Tags:[\"ln_lobby\",\"lb_status\"],billboard:\"vertical\",background:0,text:'\"\"'}}",
]
BUTTONS = [("lb_prev", tx - 2 + 0.5, "◀", "#E4E2DA"), ("lb_ready", tx + 0.5, "[ 準備就緒 ]", "#8EE07A"), ("lb_next", tx + 3 + 0.5, "▶", "#E4E2DA")]
for tag, x, label, col in BUTTONS:
    w = 1.6 if tag == "lb_ready" else 0.8
    place += [
        f"summon interaction {x} {TOP} {fz} {{Tags:[\"ln_lobby\",\"{tag}\"],width:{w}f,height:0.6f,response:1b}}",
        f"summon text_display {x} {TOP + 0.15} {fz} {{Tags:[\"ln_lobby\",\"{tag}_t\"],billboard:\"vertical\",background:1711276032,"
        f"transformation:{{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[1.2f,1.2f,1.2f]}},"
        f"text:'{jt({'text': label, 'color': col})}'}}",
    ]
# 全息微縮地形：桌面上一群發光的小方塊（之後依章節換）
rng = random.Random(3)
for i in range(26):
    hx = tx - 2 + rng.random() * 4.2
    hz = tz - 0.6 + rng.random() * 1.4
    h = 0.08 + rng.random() * 0.35
    blk = rng.choice(["light_blue_stained_glass", "cyan_stained_glass", "light_blue_stained_glass", "white_stained_glass"])
    place.append(
        f"summon block_display {hx:.2f} {TOP} {hz:.2f} {{Tags:[\"ln_lobby\"],brightness:{{sky:15,block:15}},block_state:{{Name:\"minecraft:{blk}\"}},"
        f"transformation:{{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.32f,{h:.2f}f,0.32f]}}}}")
place += ["scoreboard players set #placed ln 1", "scoreboard players set #c20 ln 20",
          "execute unless score #chap ln matches 1..8 run scoreboard players set #chap ln 5",
          "function ln:lobby/show_chap", "function ln:lobby/reset_jump"]
fn("place", place)

# ================================================================== 章節選擇
show = []
for n, name, where, start in CHAPTERS:
    tag = "可出擊" if start else "製作中"
    col = "#8EE07A" if start else "#888888"
    text = jt({"text": f"第{NUM[n - 1]}章  {name}\n", "color": "#F0E6C8"}, {"text": f"{where}\n", "color": "#A8B4BC"},
              {"text": f"● {tag}", "color": col})
    show.append(f"execute if score #chap ln matches {n} run data modify entity @e[tag=lb_chap,limit=1] text set value '{sq(text)}'")
fn("show_chap", show)
fn("sel_prev", ["scoreboard players remove #chap ln 1", "execute if score #chap ln matches ..0 run scoreboard players set #chap ln 8",
                "function ln:lobby/show_chap", "execute as @a at @s run playsound lnai:sfx.objective master @s ~ ~ ~ 0.4 1.4"])
fn("sel_next", ["scoreboard players add #chap ln 1", "execute if score #chap ln matches 9.. run scoreboard players set #chap ln 1",
                "function ln:lobby/show_chap", "execute as @a at @s run playsound lnai:sfx.objective master @s ~ ~ ~ 0.4 1.4"])
avail = [n for n, *_r, s in CHAPTERS if s]
fn("chap_ok", ["scoreboard players set #ok ln 0"] + [f"execute if score #chap ln matches {n} run scoreboard players set #ok ln 1" for n in avail])

# 準備就緒（切換）
fn("click_ready", [
    "function ln:lobby/chap_ok",
    "execute if score #ok ln matches 0 on target run tellraw @s " + jt({"text": "這一章還在製作中，請先選「可出擊」的章節。", "color": "#F0A040"}),
    "execute if score #ok ln matches 1 run function ln:lobby/toggle_ready",
])
fn("toggle_ready", [
    "execute on target if entity @s[tag=ln_ready] run tag @s add ln_unready",
    "execute on target if entity @s[tag=!ln_ready] run tag @s add ln_ready",
    "execute on target if entity @s[tag=ln_unready] run tag @s remove ln_ready",
    "execute on target run tag @s remove ln_unready",
    "execute on target at @s run playsound lnai:sfx.scanner_ready master @s ~ ~ ~ 0.6 1",
])

# 狀態文字：「準備就緒 r / p」
status = []
for p in range(1, 5):
    for r in range(0, p + 1):
        col = "#8EE07A" if r == p else "#E4E2DA"
        text = jt({"text": f"準備就緒  {r} / {p}", "color": col})
        cond = f"if score #pl ln matches {p}" if p < 4 else "if score #pl ln matches 4.."
        status.append(f"execute {cond} if score #rd ln matches {r} run data modify entity @e[tag=lb_status,limit=1] text set value '{text}'")
fn("show_status", status)

# ================================================================== 進入大廳
fn("enter", [
    "scoreboard players set #c20 ln 20",
    "execute unless score #placed ln matches 1 run function ln:lobby/place",
    f"forceload add {BX1} {BZ1} {BX2} {BZ2}",
    "lnhud cutscene @a stop",
    "function ln:ch05/cleanup",
    "scoreboard players set #lobby ln 1",
    "scoreboard players set #inch ln 0",
    "scoreboard players set #lt ln 0",
    "time set 18000", "weather clear",
    "function ln:lobby/reset_jump",
    "execute as @a run function ln:lobby/enter_one",
    "function ln:lobby/anims",
    "function ln:lobby/show_chap",
])
fn("enter_one", [
    "tag @s remove ln_ready", "tag @s remove ln_jumped", "tag @s add ln_seen",
    "gamemode adventure @s", "clear @s", "effect clear @s",
    "team join ln_blue @s",
    TP_SPAWN,
    f"spawnpoint @s {xyz(SPAWN)}",
    "lnhud tint @s 00000000 0",
    "lnhud objective @s " + "在作戰桌選擇章節，全員按「準備就緒」後出發",
])

# 上線處理：新玩家／重新連線的玩家，在大廳時直接送上飛機
fn("rejoin", [
    "scoreboard players reset @s ln_left",
    "tag @s add ln_seen",
    "execute if score #lobby ln matches 1.. run function ln:lobby/enter_one",
    "execute if score #lobby ln matches 0 unless score #inch ln matches 1 if score #placed ln matches 1 run function ln:lobby/enter",
])

# ================================================================== 跳傘
lights_red = [f"setblock {xyz(p)} shroomlight" for p in P["ceil_lights"]]
lights_norm = [f"setblock {xyz(p)} sea_lantern" for p in P["ceil_lights"]]
r1, r2 = P["rail"]
e1, e2 = P["ramp_ext"]
fn("reset_jump", lights_norm + [
    *[f"setblock {xyz(p)} redstone_lamp[lit=false]" for p in P["jump_lamps"]],
    *[f"setblock {p[0]} {p[1]} {p[2] + 1} lime_concrete" for p in P["jump_lamps"]],
    f"fill {xyz(r1)} {xyz(r2)} iron_bars",
    f"fill {xyz(e1)} {xyz(e2)} air",
    f"fill {e1[0]} {e1[1] + 1} {e1[2]} {e2[0]} {e2[1] + 1} {e2[2]} air",
])
fn("go", lights_red + [
    "scoreboard players set #lobby ln 2",
    "scoreboard players set #jt ln 0",
    "scoreboard players set #jw ln 0",
    *[f"setblock {xyz(p)} shroomlight" for p in P["jump_lamps"]],
    f"fill {xyz(e1)} {xyz(e2)} polished_andesite",                      # 跳板完全放平
    f"fill {e1[0]} {e1[1] + 1} {e1[2]} {e1[0]} {e1[1] + 1} {e2[2]} iron_bars",
    f"fill {e2[0]} {e1[1] + 1} {e1[2]} {e2[0]} {e1[1] + 1} {e2[2]} iron_bars",
    "lnhud tint @a 55B01010 30 pulse",
    "lnhud objective @a 戰鬥紅光：到機尾待命，跳傘燈轉綠就跳",
    "execute as @a at @s run playsound minecraft:block.piston.contract master @s ~ ~ ~ 1 0.5",
])
fn("green", [
    *[f"setblock {p[0]} {p[1]} {p[2] + 1} verdant_froglight" for p in P["jump_lamps"]],
    f"fill {xyz(r1)} {xyz(r2)} air",                                     # 拆掉護欄
    "lnhud tint @a 3010A040 6",
    "schedule function ln:lobby/green_off 30t replace",
    "lnhud objective @a 綠燈！從機尾跳下",
    "execute as @a at @s run playsound lnai:sfx.scanner_ready master @s ~ ~ ~ 1 0.8",
])
fn("green_off", ["lnhud tint @a[tag=!ln_jumped] 00000000 40"])
fn("jumped", [
    "tag @s add ln_jumped",
    "effect give @s slow_falling 30 0 true",
    "lnhud tint @s FF000000 15",
    "execute at @s run playsound minecraft:item.elytra.flying master @s ~ ~ ~ 0.8 1.2",
])
start_cmds = [f"execute if score #chap ln matches {n} run function {s}" for n, *_r, s in CHAPTERS if s]
fn("launch", [
    "scoreboard players set #lobby ln 0",
    "scoreboard players set #inch ln 1",
    "function ln:lobby/reset_jump",
    "tag @a remove ln_ready", "tag @a remove ln_jumped",
    "effect clear @a",
    *start_cmds,
    "lnhud tint @a 00000000 30",
    f"forceload remove {BX1} {BZ1} {BX2} {BZ2}",
])

# ================================================================== 每 tick
# 雲：機外固定的發射點，每 tick 輪流射出幾團往機尾飛的雲（從擋風玻璃和跳板看得到）
rng = random.Random(9)
EMIT = []
for i in range(48):
    side = rng.choice(["front", "left", "right", "below"])
    if side == "front":
        p = (O[0] + rng.uniform(-14, 30), FY + rng.uniform(-6, 14), O[2] + rng.uniform(-40, -6))
    elif side == "left":
        p = (O[0] + rng.uniform(-30, -3), FY + rng.uniform(-8, 10), O[2] + rng.uniform(-30, 40))
    elif side == "right":
        p = (O[0] + rng.uniform(19, 46), FY + rng.uniform(-8, 10), O[2] + rng.uniform(-30, 40))
    else:
        p = (O[0] + rng.uniform(-10, 26), FY + rng.uniform(-18, -6), O[2] + rng.uniform(-20, 50))
    EMIT.append(p)
clouds = ["scoreboard players add #cl ln 1", "execute if score #cl ln matches 16.. run scoreboard players set #cl ln 0"]
for i, (x, y, z) in enumerate(EMIT):
    clouds.append(f"execute if score #cl ln matches {i % 16} run particle minecraft:cloud {x:.1f} {y:.1f} {z:.1f} 0 0 1 1.6 0 force @a")
# 機鼻前方、兩側翼尖：較密的雲流和白色速度線（end_rod），一律往機尾（+z）高速飛過，每 tick 只多 2 顆
STREAK = []
for i in range(16):
    STREAK.append((O[0] + 8 + rng.uniform(-6, 6), FY + rng.uniform(-1, 9), O[2] - rng.uniform(10, 24), "cloud", 1.2))
for i in range(16):
    sx = rng.choice([rng.uniform(-30, -14), rng.uniform(30, 46)])
    STREAK.append((O[0] + sx, FY + 8 + rng.uniform(-3, 3), O[2] + rng.uniform(0, 18), "end_rod", 2.2))
for i, (x, y, z, kind, spd) in enumerate(STREAK):
    clouds.append(f"execute if score #cl ln matches {i % 16} run particle minecraft:{kind} {x:.1f} {y:.1f} {z:.1f} 0 0 1 {spd} 0 force @a")
fn("clouds", clouds)

fn("tick", [
    # 上線處理（新玩家、重新連線）
    "execute as @a[tag=!ln_seen] run function ln:lobby/rejoin",
    "execute as @a[scores={ln_left=1..}] run function ln:lobby/rejoin",
    "execute if score #lobby ln matches 1.. run function ln:lobby/active",
])
fn("active", [
    "function ln:lobby/clouds",
    "scoreboard players add #lt ln 1",
    "execute if score #lt ln matches 200.. run function ln:lobby/anims",
    "execute if score #lt ln matches 200.. run scoreboard players set #lt ln 0",
    # 按鈕
    "execute as @e[tag=lb_prev] if data entity @s interaction run function ln:lobby/sel_prev",
    "execute as @e[tag=lb_next] if data entity @s interaction run function ln:lobby/sel_next",
    "execute as @e[tag=lb_ready] if data entity @s interaction run function ln:lobby/click_ready",
    "data remove entity @e[tag=lb_prev,limit=1] interaction",
    "data remove entity @e[tag=lb_next,limit=1] interaction",
    "data remove entity @e[tag=lb_ready,limit=1] interaction",
    # 人數與準備
    "execute store result score #pl ln if entity @a[gamemode=adventure]",
    "execute store result score #rd ln if entity @a[gamemode=adventure,tag=ln_ready]",
    "function ln:lobby/show_status",
    "execute if score #lobby ln matches 1 if score #pl ln matches 1.. if score #rd ln = #pl ln run function ln:lobby/go",
    # 還不能跳的時候掉出去 → 拉回機艙
    f"execute if score #lobby ln matches 1 as @a[{in_lobby()}] at @s if entity @s[y={FY - 60},dy={60 - 3}] run function ln:lobby/caught",
    "execute if score #lobby ln matches 2 run function ln:lobby/jump_tick",
])
fn("caught", [TP_SPAWN, "tellraw @s " + jt({"text": "還沒到跳傘時間！", "color": "#F0A040"})])
fn("jump_tick", [
    "scoreboard players add #jt ln 1",
    "scoreboard players operation #jm ln = #jt ln",
    "scoreboard players operation #jm ln %= #c20 ln",
    "execute if score #jm ln matches 0 as @a at @s run playsound lnai:sfx.jump_alarm master @s ~ ~ ~ 0.7 1",
    f"execute if score #jt ln matches {GREEN_AT} run function ln:lobby/green",
    # 綠燈前掉下去（理論上有護欄）也拉回
    f"execute if score #jt ln matches ..{GREEN_AT - 1} as @a[{in_lobby()}] at @s if entity @s[y={FY - 60},dy={60 - 3}] run function ln:lobby/caught",
    f"execute if score #jt ln matches {GREEN_AT}.. as @a[{in_lobby()},tag=!ln_jumped] at @s if entity @s[y={FY - 60},dy={60 - 3}] run function ln:lobby/jumped",
    "execute store result score #jd ln if entity @a[gamemode=adventure,tag=ln_jumped]",
    # 全員跳下 → 等畫面全黑（20 tick）再出發；或綠燈後等太久就直接出發
    "execute if score #jd ln = #pl ln unless score #jw ln matches 1.. run scoreboard players set #jw ln 1",
    "execute if score #jw ln matches 1.. run scoreboard players add #jw ln 1",
    "execute if score #jw ln matches 22.. run function ln:lobby/launch_now",
    f"execute if score #jt ln matches {GREEN_AT + LAUNCH_TIMEOUT}.. run function ln:lobby/launch_now",
])
fn("launch_now", ["scoreboard players set #jw ln 0", "function ln:lobby/launch"])

# 開發用：一鍵進大廳
fn("help", ["tellraw @s " + jt({"text": "大廳：/function ln:lobby/place（重建飛機）、/function ln:lobby/enter（全員上機）", "color": "#7FC8E8"})])

# ================================================================== 輸出
OUT.mkdir(parents=True, exist_ok=True)
for old in OUT.glob("*.mcfunction"):
    old.unlink()
for name, lines in files.items():
    (OUT / f"{name}.mcfunction").write_text("# 由 tools/build_lobby.py 自動產生，請勿手動修改\n" + "\n".join(lines) + "\n", encoding="utf-8")
print(f"大廳：{len(files)} 個函式 → {OUT.relative_to(ROOT)}")
