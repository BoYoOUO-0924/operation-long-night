"""第一章：雷霆空降 —— 把 levels/ch01.json ＋ 黑石海岸錨點編譯成資料包函式。

執行：python tools/build_ch01.py
產生：datapack/longnight/data/ln/functions/ch01/**（請勿手動修改這些檔案）

階段（#stage ln，#run ln = 1 表示目前在第一章）：
  1 降落（傘降、探照燈）   2 搶灘（探照燈電纜、防空砲）   3 破解大門（狐狸 10 秒）
  4 雷達（三座 C4、倒數）  5 撤離（艦隊打擊、山體異變、守夜人、懸崖觀測站）
"""
import json
import math
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
PACK = ROOT / "datapack/longnight/data/ln/functions"
OUT = PACK / "ch01"
NS = "ln:ch01"
A = json.loads((ROOT / "generators/out/blackstone_coast.json").read_text(encoding="utf-8"))
L = json.loads((ROOT / "levels/ch01.json").read_text(encoding="utf-8"))
HM = json.loads((ROOT / "generators/out/heightmap_ch01.json").read_text(encoding="utf-8"))
SPK = L["speakers"]
TPS = 20
FONT = "lnai:ui"
P = "@a[gamemode=adventure]"

files = {}


def fn(name, lines):
    files[name] = "# 由 tools/build_ch01.py 自動產生，請勿手動修改\n" + "\n".join(lines) + "\n"


def xyz(p):
    return f"{p[0]} {p[1]} {p[2]}"


def jtext(obj):
    if isinstance(obj, list):
        obj = {"text": "", "font": FONT, "extra": obj}
    elif isinstance(obj, dict) and "font" not in obj:
        obj = {**obj, "font": FONT}
    return json.dumps(obj, ensure_ascii=False)


def surf(x, z):
    return HM["solid"][z - HM["z1"]][x - HM["x1"]] + 1


def norm(text):
    return text.replace("：", ": ").replace("！", "! ").replace("，", ", ").replace("？", "? ")


SUB_COLOR = {"aqua": "#7FC8D8", "gold": "#E0B050", "green": "#8CC08C", "gray": "#B4B4B4",
             "dark_red": "#D05050", "yellow": "#FFB020", "dark_aqua": "#5BA8B0", "white": "#E4E2DA"}


def say_line(who, text):
    text = norm(text).strip()
    color = SPK.get(who, "white")
    if who == "目標":
        return [f"tellraw @a {jtext([{'text': '▶ 目標：', 'color': color, 'bold': True}, {'text': text, 'color': 'white'}])}",
                f"lnhud objective @a {text}",
                "execute as @a at @s run playsound lnai:sfx.objective master @s ~ ~ ~ 0.8 1"]
    if who == "提示":
        return [f"tellraw @a {jtext([{'text': '（提示）', 'color': color}, {'text': text, 'color': 'gray', 'italic': True}])}"]
    dur = max(70, min(240, 40 + len(text) * 5))
    hexc = SUB_COLOR.get(color, "#E4E2DA").lstrip("#")
    return [f'lnhud say @a {hexc} {dur} "{who}" {text}']


def dialogue(key):
    """跟著階段計時器 #t 播放；回傳最後一句的 tick"""
    lines = []
    for d in L["dialogue"][key]:
        t = int(d["at"] * TPS)
        for cmd in say_line(d["who"], d["text"]):
            lines.append(f"execute if score #t ln matches {t} run {cmd}")
    fn(f"dlg/{key}", lines)
    return int(max(d["at"] for d in L["dialogue"][key]) * TPS)


def event(key):
    """事件對白：第一句立刻播，其餘排程。回傳啟動指令"""
    start = []
    for i, d in enumerate(L["dialogue"][key]):
        name = f"evdlg/{key}_{i}"
        fn(name, say_line(d["who"], d["text"]))
        t = int(d["at"] * TPS)
        start.append(f"function {NS}/{name}" if t == 0 else f"schedule function {NS}/{name} {t}t append")
    fn(f"evdlg/{key}", start)
    return f"function {NS}/evdlg/{key}"


def bossbar(name, color="yellow"):
    return [f"bossbar set ln:obj name {jtext({'text': name})}", f"bossbar set ln:obj color {color}"]


def goto(stage):
    return [f"scoreboard players set #stage ln {stage}", "scoreboard players set #t ln 0"]


def wp(p, r=3, hunt=None):
    h = f",ln_hunt:{hunt}" if hunt is not None else ""
    return f"{{ForgeData:{{ln_wp:[I;{p[0]},{p[1]},{p[2]}],ln_wpr:{r}{h}}}}}"


def label(tag, p, text, color="#F0A040", scale=2.5, dy=1.6):
    return (f'summon text_display {p[0] + 0.5} {p[1] + dy} {p[2] + 0.5} {{Tags:["ln","{tag}"],billboard:"center",see_through:1b,'
            f"transformation:{{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[{scale}f,{scale}f,{scale}f]}},"
            f"brightness:{{sky:15,block:15}},background:1711276032,text:'{jtext({'text': text, 'color': color})}'}}")


def button(tag, p, w=1.4, h=1.4):
    return f'summon interaction {p[0] + 0.5} {p[1]} {p[2] + 0.5} {{Tags:["ln","{tag}"],width:{w}f,height:{h}f,response:1b}}'


def target(tag, p, size=1):
    """可射擊的目標：隱形的豬（史萊姆是敵對生物，會被隊友 NPC 一直射）。命中判定看血量有沒有少"""
    return (f'summon pig {p[0] + 0.5} {p[1]} {p[2] + 0.5} {{Tags:["ln","{tag}"],NoAI:1b,NoGravity:1b,Silent:1b,'
            f'PersistenceRequired:1b,Invulnerable:0b,DeathLootTable:"minecraft:empty",Health:1000f,'
            f'Attributes:[{{Name:"generic.max_health",Base:1000d}}],ActiveEffects:[{{Id:14,Duration:-1,Amplifier:0b,ShowParticles:0b}}]}}')


def boom(p, big=True):
    return [f"particle minecraft:{'explosion_emitter' if big else 'explosion'} {xyz(p)} 1 1 1 0 {2 if big else 6} force @a",
            f"particle minecraft:large_smoke {xyz(p)} 1.5 1.5 1.5 0.05 40 force @a",
            f"particle minecraft:lava {xyz(p)} 1 1 1 0 20 force @a",
            f"playsound lnai:sfx.boom master @a {xyz(p)} 6 0.9",
            f"playsound minecraft:entity.generic.explode master @a {xyz(p)} 4 0.7"]


# ================================================================== 裝備外觀
DRESS_LATER = "schedule function ln:ch05/dress 2t replace"     # 沿用第五章的換裝函式（依模板穿 ZeroContact）
PLAYER_GEAR = ("helmet_airframe", "armor_defender_2")

# ================================================================== 隊友（傘降時就在空中，跟著玩家）
ALLIES = [("ln_baiya", "白鴉", "aqua", "blue_sniper", 1), ("ln_tank", "戰車", "gold", "blue_support", 2),
          ("ln_fox", "狐狸", "green", "blue_assault", 3)]
BEACON = A["beacon"]
DROP = [(122, 300, 1406), (126, 300, 1414), (122, 300, 1422), (128, 300, 1428)]   # 緩降約每秒 6 格 → 約 40 秒落地


def summon_ally(tag, name, color, template, slot, pos):
    nbt = (f'{{template:"{template}",CustomName:\'{jtext({"text": name, "color": color})}\',CustomNameVisible:1b,'
           f'Invulnerable:1b,PersistenceRequired:1b,Tags:["ln","ln_ally","{tag}","ln_new","ln_dress"],'
           f'ForgeData:{{ln_side:"blue",ln_follow:1b,ln_slot:{slot},ln_hunt:24}}}}')
    return f"summon tacznpcs:npc {pos} {nbt}"


fn("spawn_allies", [summon_ally(*a, pos=f"{BEACON[0] + 6 + 3 * i} 280 {BEACON[2] - 4 + 4 * i}") for i, a in enumerate(ALLIES)] + [
    "team join ln_blue @e[tag=ln_new]",
    "effect give @e[tag=ln_new] glowing infinite 0 true",
    "effect give @e[tag=ln_new] slow_falling 120 0 true",
    "tag @e[tag=ln_new] remove ln_new",
    DRESS_LATER,
])

# ================================================================== 敵人（小隊；lnai 模組負責 AI）
SPAWNS = A["enemy_spawns"]
COMPS = [["red_assault", "red_assault", "red_support", "red_assault"],
         ["red_assault", "red_cqb", "red_cqb", "red_support"],
         ["red_assault", "red_sniper", "red_support", "red_assault"]]
ROUTE_NAMES = list(SPAWNS)


def enemy_nbt(route, template, slot, hunt=24):
    return (f'{{template:"{template}",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_{route}"],'
            f'ForgeData:{{ln_side:"red",ln_slot:{slot},ln_hunt:{hunt}}}}}')


for route, (x, z) in SPAWNS.items():
    lines = []
    for ci, comp in enumerate(COMPS):
        for slot, tpl in enumerate(comp[:3]):
            lines.append(f"execute if score #comp ln matches {ci} run summon tacznpcs:npc {x} 250 {z} {enemy_nbt(route, tpl, slot)}")
        lines.append(f"execute if score #comp ln matches {ci} if score #players ln matches 3.. run "
                     f"summon tacznpcs:npc {x} 250 {z} {enemy_nbt(route, comp[3], 3)}")
    lines += [f"spreadplayers {x} {z} 1 5 false @e[tag=ln_new]", DRESS_LATER, "team join ln_red @e[tag=ln_new]"]
    for i, text in enumerate(L["callouts"][route]):
        for cmd in say_line(L["callout_speakers"][route], text):
            lines.append(f"execute if score #flip ln matches {i} if score #callout ln matches 1 run {cmd}")
    lines += ["scoreboard players add #comp ln 1", "execute if score #comp ln matches 3.. run scoreboard players set #comp ln 0",
              "scoreboard players add #flip ln 1", "execute if score #flip ln matches 2.. run scoreboard players set #flip ln 0",
              "tag @e[tag=ln_new] add ln_fresh", "tag @e[tag=ln_new] remove ln_new"]
    fn(f"sq/{route}", lines)


def squad(route, goal=None, hunt=24, callout=True):
    """派一組人；goal = 集結點（沒有就守在出生點附近）"""
    out = [f"scoreboard players set #callout ln {1 if callout else 0}", f"function {NS}/sq/{route}"]
    if goal is not None:
        out.append(f"execute as @e[tag=ln_fresh] run data merge entity @s {wp(goal, 4, hunt)}")
    out.append("tag @e[tag=ln_fresh] remove ln_fresh")
    return out


# 導演（雷達階段）：輪流從 5 個出生點派兵，往最近的玩家搜索
director = ["scoreboard players add #dt ln 1"]
for i, route in enumerate(ROUTE_NAMES):
    director.append(f"execute if score #dt ln matches 500.. if score #alive ln < #max ln if score #route ln matches {i} run function {NS}/sq/{route}")
director += [
    "execute as @e[tag=ln_fresh] run data merge entity @s {ForgeData:{ln_hunt:64}}",
    "tag @e[tag=ln_fresh] remove ln_fresh",
    "execute if score #dt ln matches 500.. if score #alive ln < #max ln run scoreboard players add #route ln 1",
    f"execute if score #route ln matches {len(ROUTE_NAMES)}.. run scoreboard players set #route ln 0",
    "execute if score #dt ln matches 500.. run scoreboard players set #dt ln 0",
]
fn("director", director)

# ================================================================== 探照燈（block_display 光束，掃到玩家 2 秒就引來高射砲）
LAMP1 = (A["searchlight"][0] + 1.5, A["searchlight"][1] + 0.5, A["searchlight"][2] + 0.5)
LAMP2 = (A["radar_c"][0] + 0.5, A["radar_c"][1] + 1.5, A["radar_c"][2] + 0.5)      # 燈塔頂（第一階段才有）
PERIOD = 160


def ray(o, yaw, pitch, d):
    ry, rp = math.radians(yaw), math.radians(pitch)
    return (o[0] - math.sin(ry) * math.cos(rp) * d, o[1] - math.sin(rp) * d, o[2] + math.cos(ry) * math.cos(rp) * d)


def sweep(k, mode):
    """回傳這一刻各光束的 (原點, yaw, pitch)"""
    a = 2 * math.pi * k / PERIOD
    if mode == 1:      # 第一階段：兩道光束往天空掃（玩家在空中）
        return [(LAMP1, -90 + 38 * math.sin(a), -48 + 14 * math.sin(2 * a)),
                (LAMP2, -160 + 30 * math.sin(a + 1.7), -28 + 10 * math.sin(2 * a + 0.5))]
    return [(LAMP1, -90 + 52 * math.sin(a), 46 + 10 * math.sin(2 * a))]   # 第二階段：往下掃沙灘和崖壁小路


for mode in (1, 2):
    disp = []
    for k in range(PERIOD):
        body = []
        for bi, (o, yaw, pitch) in enumerate(sweep(k, mode)):
            body.append(f"tp @e[tag=c1_beam{bi}] {o[0]:.2f} {o[1]:.2f} {o[2]:.2f} {yaw:.1f} {pitch:.1f}")
            for d in range(8, 72, 7):
                px, py, pz = ray(o, yaw, pitch, d)
                body.append(f"execute positioned {px:.1f} {py:.1f} {pz:.1f} as {P.replace(']', ',distance=..4.5]')} run scoreboard players add @s ln_lit 3")
        fn(f"sl{mode}/k{k}", body)
        disp.append(f"execute if score #sk ln matches {k} run function {NS}/sl{mode}/k{k}")
    fn(f"sl{mode}/tick", ["scoreboard players add #sk ln 1", f"execute if score #sk ln matches {PERIOD}.. run scoreboard players set #sk ln 0",
                          *disp,
                          "scoreboard players remove @a[scores={ln_lit=1..}] ln_lit 1",
                          f"execute as @a[scores={{ln_lit=40..}}] at @s run function {NS}/flak"])


def beam(i, o):
    return (f'summon block_display {o[0]} {o[1]} {o[2]} {{Tags:["ln","c1_beam{i}"],brightness:{{sky:15,block:15}},view_range:4f,'
            f'block_state:{{Name:"minecraft:white_stained_glass"}},'
            f'transformation:{{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[-0.45f,-0.45f,0f],scale:[0.9f,0.9f,70f]}}}}')


fn("flak", [
    "scoreboard players set @s ln_lit -60",                 # 冷卻 3 秒
    "effect give @s glowing 5 0 true",
    "playsound lnai:sfx.jump_alarm master @s ~ ~ ~ 0.8 1.3",
    "particle minecraft:explosion ~ ~1 ~ 4 3 4 0 5 force @a",
    "particle minecraft:large_smoke ~ ~1 ~ 4 3 4 0.02 30 force @a",
    "playsound minecraft:entity.generic.explode master @a ~ ~ ~ 3 0.8",
    "lnhud tint @s 60FFFFFF 12 flash",
    "damage @s 2 minecraft:explosion",
    f"execute if score #litsaid ln matches 0 run {event('evt_lit')}",
    "scoreboard players set #litsaid ln 1",
])

# ================================================================== 傘降（每位玩家一頂傘，用 ln_pid 配對）
CHUTE = ('{{Tags:["ln","c1_chute_e","c1_chute_{k}"],view_range:3f,block_state:{{Name:"minecraft:green_terracotta"}},'
         'transformation:{{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[-1.6f,2.7f,-1.2f],scale:[3.2f,0.35f,2.4f]}}}}')
LINES = ('{{Tags:["ln","c1_chute_e","c1_chute_{k}"],view_range:3f,block_state:{{Name:"minecraft:chain",Properties:{{axis:"y"}}}},'
         'transformation:{{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[-1.4f,1.2f,-1.0f],scale:[2.8f,1.5f,2.0f]}}}}')
chute = []
for k in range(1, 5):
    chute.append(f"execute as @a[tag=c1_chute,scores={{ln_pid={k}}}] at @s run tp @e[tag=c1_chute_{k}] ~ ~ ~ ~ 0")
chute += [
    # 落水：浪把人推上岸
    f"execute as @a[tag=c1_chute] at @s if block ~ ~ ~ water run tp @s {BEACON[0]} {BEACON[1]} {BEACON[2]}",
    f"execute as @a[tag=c1_chute] at @s unless block ~ ~-0.3 ~ air unless block ~ ~-0.3 ~ water run function {NS}/land",
]
fn("chute", chute)
fn("land", [
    "tag @s remove c1_chute",
    "effect clear @s slow_falling",
    *[f"execute if score @s ln_pid matches {k} run kill @e[tag=c1_chute_{k}]" for k in range(1, 5)],
    "playsound minecraft:item.armor.equip_leather master @a ~ ~ ~ 1 0.7",
    "particle minecraft:poof ~ ~0.2 ~ 0.6 0.1 0.6 0.02 12",
    "scoreboard players add #landed ln 1",
])

# ================================================================== 流程
fn("cleanup", [
    "lnhud music @a stop 60",
    "lnhud ambient @a stop 60",
    "kill @e[tag=ln]",
    "lnglass restore",
    "scoreboard players set #stage ln 0",
    "scoreboard players set #run ln 0",
    "bossbar set ln:obj visible false",
    "effect clear @a",
    "tag @a remove c1_chute",
    "lnhud objective @a",
    "lnhud waypoint @a clear",
    "gamerule naturalRegeneration true",
    f"schedule clear {NS}/to_lobby",
    f"schedule clear {NS}/sniper_down",
])
fn("loadout", [
    f"lnkit restore {P} m4a1 glock_17",
    f"item replace entity {P} hotbar.2 with superbwarfare:knife",
    f"item replace entity {P} hotbar.3 with superbwarfare:hand_grenade 2",
    f"item replace entity {P} hotbar.4 with lnai:bandage 4",
    f"lnkit ammo {P} 4 2 add",
    f"give {P} lnai:painkiller 2",
    f"give {P} lnai:medkit 2",
    f"give {P} superbwarfare:m18_smoke_grenade 1",
    f"item replace entity {P} armor.head with zerocontact:{PLAYER_GEAR[0]}",
    f"item replace entity {P} armor.chest with zerocontact:{PLAYER_GEAR[1]}",
    f"effect give {P} saturation infinite 0 true",
    f"execute as {P} run function ln:lobby/kit_extras",
])
box = A["box"]
for k in range(1, 5):
    fn(f"pid_{k}", [f"scoreboard players set @s ln_pid {k}", "tag @s remove c1_nopid"])
fn("start", [
    "function ln:ch05/cleanup",
    f"function {NS}/cleanup",
    f"forceload add {box[0]} {box[1]} {box[2]} {box[3]}",
    "execute positioned 0 0 0 run function ln:build/coast_battery",
    "kill @e[type=item]",
    "time set 18000",
    "weather rain 1000000",
    "scoreboard objectives add ln_lit dummy",
    "scoreboard objectives add ln_pid dummy",
    "scoreboard players set @a ln_lit 0",
    "scoreboard players reset @a ln_pid",
    "scoreboard players set #k ln 0",
    "gamemode adventure @a",
    "gamerule naturalRegeneration false",
    "team join ln_blue @a",
    "clear @a",
    f"function {NS}/loadout",
    # 每人編號（1～4）：配對降落傘
    f"tag {P} add c1_nopid",
    *[f"execute as @a[tag=c1_nopid,limit=1,sort=random] run function {NS}/pid_{k}" for k in range(1, 5)],
    "tag @a remove c1_nopid",
    *[f"tp @a[scores={{ln_pid={k}}}] {xyz(DROP[k - 1])} 90 20" for k in range(1, 5)],
    *[f"execute if entity @a[scores={{ln_pid={k}}}] run summon block_display {xyz(DROP[k - 1])} " + CHUTE.format(k=k) for k in range(1, 5)],
    f"tag {P} add c1_chute",
    f"effect give {P} slow_falling infinite 0 true",
    f"spawnpoint @a {xyz(BEACON)}",
    beam(0, LAMP1), beam(1, LAMP2),
    f"function {NS}/spawn_allies",
    "bossbar set ln:obj players @a",
    "bossbar set ln:obj visible true",
    "bossbar set ln:obj max 1",
    "bossbar set ln:obj value 1",
    *bossbar("目標：降落到沙灘"),
    f"lnhud waypoint @a {xyz(BEACON)}",
    # 信標：沙灘上閃綠光（只有目鏡看得到 → 就是 HUD 導航點＋綠色粒子）
    'summon marker ' + xyz(BEACON) + ' {Tags:["ln","c1_beacon"]}',
    "scoreboard players set #litsaid ln 0",
    "scoreboard players set #landed ln 0",
    "scoreboard players set #c1lt ln 0",
    "scoreboard players set #sk ln 0",
    "scoreboard players set #run ln 1",
    *goto(1),
    "lnhud tint @a 00000000 30",
    "lnhud ambient @a stop 20",
])
fn("stop", [f"function {NS}/cleanup", "gamemode creative @a", f"tellraw @a {jtext({'text': '[長夜] 已中止第一章。', 'color': 'red'})}"])

# ---- 1 降落
dialogue("drop")
fn("s1", [
    f"function {NS}/dlg/drop",
    f"function {NS}/chute",
    f"function {NS}/sl1/tick",
    "execute as @e[tag=c1_beacon] at @s run particle minecraft:dust 0.2 1 0.3 2 ~ ~0.5 ~ 0.2 0.6 0.2 0 4 force @a",
    "execute as @e[tag=c1_beacon] at @s run particle minecraft:end_rod ~ ~1 ~ 0.1 2 0.1 0.01 2 force @a",
    "execute as @a at @s run particle minecraft:rain ~ ~3 ~ 8 3 8 0 20 normal @s",
    # 全員落地，或第一個人落地 20 秒後 → 搶灘
    f"execute unless entity @a[tag=c1_chute] run function {NS}/to_s2",
    "execute if score #landed ln matches 1.. run scoreboard players add #c1lt ln 1",
    f"execute if score #c1lt ln matches 400.. run function {NS}/force_land",
    f"execute if score #t ln matches 2400.. run function {NS}/force_land",
])
fn("force_land", [f"tp @a[tag=c1_chute] {BEACON[0]} {BEACON[1]} {BEACON[2]}",
                  f"execute as @a[tag=c1_chute] at @s run function {NS}/land", f"function {NS}/to_s2"])

# ---- 2 搶灘：探照燈電纜＋防空砲
SL = A["searchlight"]
CABLE = A["searchlight_cable"]
AA = A["aa_gun"]
BAR = A["aa_barrels"]
fn("to_s2", [
    *goto(2),
    "scoreboard players set #c1lt ln 0",
    "kill @e[tag=c1_beam1]",
    "kill @e[tag=c1_beacon]",
    "kill @e[tag=c1_chute_e]",
    "effect clear @e[tag=ln_ally] slow_falling",
    event("landed"),
    "scoreboard players set #light ln 0",
    "scoreboard players set #aa ln 0",
    "scoreboard players set #cable ln 0",
    "scoreboard players set #bar ln 0",
    "scoreboard players set #scan ln 0",
    "scoreboard players set #aaf ln 0",
    "execute store result score #players ln if entity @a[gamemode=adventure]",
    target("c1_cable", CABLE), target("c1_barrels", BAR),
    button("c1_aa_btn", AA, 1.6, 1.6),
    label("c1_aa_lbl", AA, "安裝 C4（右鍵）", dy=2.2),
    *squad("shelf_south", goal=(60, surf(60, 1420), 1420), hunt=22, callout=False),
    *squad("gate_inside", goal=(66, surf(66, 1406), 1406), hunt=22, callout=False),
    f"lnhud waypoint @a {xyz(A['path_bottom'])}",
    *bossbar("目標：破壞探照燈和防空砲"),
    "lnhud music @a ch05_suspense 60",
])
dialogue("beach")
fn("s2", [
    f"function {NS}/dlg/beach",
    f"execute if score #light ln matches 0 run function {NS}/sl2/tick",
    # 爬到崖頂後導航點換成探照燈
    f"execute if score #t ln matches 20.. positioned {xyz(A['path_top'])} if entity @a[distance=..6] run lnhud waypoint @a {xyz(SL)}",
    # 狐狸的脈衝掃描：接近燈塔時第一次，之後每 20 秒
    f"execute if score #scan ln matches 0 positioned {xyz(SL)} if entity {P.replace(']', ',distance=..30]')} run function {NS}/scan_first",
    "execute if score #scan ln matches 1.. run scoreboard players add #scan ln 1",
    f"execute if score #scan ln matches 400.. run function {NS}/scan",
    # 電纜：打中 3 下
    f"execute as @e[tag=c1_cable] run function {NS}/hit_cable",
    f"execute if score #light ln matches 0 if score #cable ln matches 3.. run function {NS}/light_out",
    # 防空砲：打油料桶 2 下，或在砲座按 C4（5 秒後爆炸）
    f"execute as @e[tag=c1_barrels] run function {NS}/hit_barrels",
    f"execute if score #aa ln matches 0 if score #bar ln matches 2.. run function {NS}/aa_down",
    f"execute as @e[tag=c1_aa_btn] if data entity @s interaction run function {NS}/aa_plant",
    "execute if score #aaf ln matches 1.. run scoreboard players remove #aaf ln 1",
    f"execute if score #aaf ln matches 1.. run particle minecraft:dust 1 0 0 1.5 {xyz(AA)} 0.2 0.2 0.2 0 2 force @a",
    f"execute if score #aa ln matches 0 if score #aaf ln matches 1 run function {NS}/aa_down",
    # 兩個都完成 → 破解大門
    f"execute if score #light ln matches 1 if score #aa ln matches 1 run function {NS}/to_s3",
])
for nm, sc, fx in (("cable", "#cable", "electric_spark"), ("barrels", "#bar", "lava")):
    fn(f"hit_{nm}", [
        "execute store result score #h ln run data get entity @s Health",
        f"execute if score #h ln matches ..999 run scoreboard players add {sc} ln 1",
        f"execute if score #h ln matches ..999 at @s run particle minecraft:{fx} ~ ~0.5 ~ 0.3 0.3 0.3 0.2 15 force @a",
        f"execute if score #h ln matches ..999 at @s run playsound minecraft:block.anvil.land master @a ~ ~ ~ 0.6 1.8",
        "execute if score #h ln matches ..999 run data modify entity @s Health set value 1000f",
    ])
fn("scan_first", ["scoreboard players set #scan ln 1", event("evt_scan"), f"function {NS}/scan",
                  label("c1_cable_lbl", CABLE, "⚡ 供電電纜（射擊）", "#7FD8FF", 2.0, 1.2)])
fn("scan", [
    "scoreboard players set #scan ln 1",
    "execute as @a at @s run playsound lnai:sfx.scanner_pulse master @s ~ ~ ~ 0.7 1",
    f"execute positioned {xyz(SL)} run effect give @e[tag=ln_enemy,distance=..70] glowing 6 0 true",
    ])
fn("light_out", [
    "scoreboard players set #light ln 1",
    "kill @e[tag=c1_beam0]", "kill @e[tag=c1_cable]", "kill @e[tag=c1_cable_lbl]",
    f"setblock {SL[0]} {SL[1]} {SL[2]} redstone_lamp[lit=false]",
    f"setblock {SL[0] + 1} {SL[1]} {SL[2]} gray_concrete",
    f"particle minecraft:electric_spark {xyz(CABLE)} 0.5 0.5 0.5 0.3 60 force @a",
    f"playsound minecraft:block.beacon.deactivate master @a {xyz(SL)} 3 0.6",
    event("evt_light_out"),
    f"execute if score #aa ln matches 0 run lnhud waypoint @a {xyz(AA)}",
])
fn("aa_plant", [
    "data remove entity @s interaction",
    "execute if score #aaf ln matches 0 if score #aa ln matches 0 run scoreboard players set #aaf ln 100",
    "kill @e[tag=c1_aa_lbl]",
    f"playsound minecraft:block.note_block.bit master @a {xyz(AA)} 2 1.6",
    f"title @a actionbar {jtext({'text': 'C4 已安裝，5 秒後引爆——快離開！', 'color': '#F0A040'})}",
])
fn("aa_down", [
    "scoreboard players set #aa ln 1",
    "scoreboard players set #aaf ln 0",
    "kill @e[tag=c1_barrels]", "kill @e[tag=c1_aa_btn]", "kill @e[tag=c1_aa_lbl]",
    *boom(AA),
    f"fill {AA[0] - 1} {AA[1] - 1} {AA[2] - 2} {AA[0] + 5} {AA[1] + 5} {AA[2] + 2} air replace end_rod",
    f"setblock {AA[0]} {AA[1] - 1} {AA[2]} campfire[lit=true]",
    f"setblock {AA[0]} {AA[1]} {AA[2]} air",
    f"fill {BAR[0]} {BAR[1]} {BAR[2] - 1} {BAR[0] + 1} {BAR[1] + 1} {BAR[2]} black_concrete replace red_concrete",
    f"execute positioned {xyz(AA)} run kill @e[tag=ln_enemy,distance=..5]",
    event("evt_aa_down"),
    f"execute if score #light ln matches 0 run lnhud waypoint @a {xyz(SL)}",
])

# ---- 3 破解大門（狐狸 10 秒）
G = A["gate"]
PANEL = A["gate_panel"]
fn("to_s3", [
    *goto(3),
    event("evt_hack"),
    f"tp @e[tag=ln_fox] {PANEL[0]} {PANEL[1] - 1} {PANEL[2] + 1}",
    "execute as @e[tag=ln_fox] run data merge entity @s {ForgeData:{ln_follow:0b}}",
    f"lnhud waypoint @a {xyz(PANEL)}",
    "bossbar set ln:obj max 200",
    "bossbar set ln:obj value 0",
    *bossbar("狐狸正在破解大門電子鎖……", "blue"),
    *squad("shelf_south", goal=(PANEL[0], PANEL[1] - 1, PANEL[2] + 6), hunt=40),
])
fn("s3", [
    "execute store result bossbar ln:obj value run scoreboard players get #t ln",
    f"execute if score #t ln matches 1.. run particle minecraft:electric_spark {xyz(PANEL)} 0.2 0.2 0.2 0.1 2 force @a",
    "scoreboard players operation #tm ln = #t ln",
    "scoreboard players operation #tm ln %= #c20 ln",
    f"execute if score #tm ln matches 0 run playsound minecraft:block.note_block.hat master @a {xyz(PANEL)} 1.5 1.8",
    f"execute if score #t ln matches 200 run function {NS}/gate_open",
])
fn("gate_open", [
    f"fill {G[0]} {G[1]} {G[2]} {G[3]} {G[4]} {G[5]} air",
    f"playsound minecraft:block.iron_door.open master @a {xyz(PANEL)} 3 0.5",
    f"playsound minecraft:block.piston.contract master @a {xyz(PANEL)} 3 0.6",
    event("evt_gate_open"),
    "execute as @e[tag=ln_fox] run data merge entity @s {ForgeData:{ln_follow:1b}}",
    f"function {NS}/to_s4",
])

# ---- 4 三座雷達（倒數 12 分鐘；失敗重設 5 分鐘）
RADARS = {"a": (A["c4_a"], A["radar_a_box"], [A["radar_a"]]),
          "b": (A["c4_b"], A["radar_b_box"], [A["radar_b"]]),
          "c": (A["c4_c"], A["radar_c_box"], [A["radar_c"]])}
NAMES = {"a": "北崖雷達", "b": "中央雷達", "c": "燈塔雷達"}
NEAREST = {"a": "plateau_north", "b": "plateau_west", "c": "south_cape"}
FULL = 12 * 60 * TPS
RETRY = 5 * 60 * TPS


def radar_wp():
    """導航點：還沒炸的雷達中第一座（玩家仍可自由決定順序）"""
    out = ["lnhud waypoint @a clear"]
    for r in ("c", "b", "a"):
        out.append(f"execute unless score #r{r} ln matches 2 run lnhud waypoint @a {xyz(RADARS[r][0])}")
    return out


arm = []
for r, (c4, bx, _) in RADARS.items():
    arm += [f"execute unless score #r{r} ln matches 2 run {button(f'c1_c4{r}', c4, 1.6, 1.8)}",
            f"execute unless score #r{r} ln matches 2 run {label(f'c1_lbl{r}', c4, NAMES[r] + '：安裝 C4（右鍵）', dy=2.4)}",
            f"execute unless score #r{r} ln matches 2 run scoreboard players set #r{r} ln 0"]
fn("arm", ["kill @e[tag=c1_c4a]", "kill @e[tag=c1_c4b]", "kill @e[tag=c1_c4c]", "kill @e[tag=c1_lbla]", "kill @e[tag=c1_lblb]", "kill @e[tag=c1_lblc]", *arm])
SNIPER = A["lighthouse_sniper"]
fn("to_s4", [
    *goto(4),
    f"function {NS}/arm",
    "execute unless score #count ln matches 0.. run scoreboard players set #count ln 0",
    "execute store result score #players ln if entity @a[gamemode=adventure]",
    "execute if score #players ln matches ..0 run scoreboard players set #players ln 1",
    "scoreboard players operation #max ln = #players ln",
    "scoreboard players set #k ln 3",
    "scoreboard players operation #max ln *= #k ln",
    "scoreboard players add #max ln 5",
    "scoreboard players set #dt ln 300",
    "scoreboard players set #route ln 0",
    f"execute unless score #rc ln matches 2 unless entity @e[tag=c1_sniper] run summon tacznpcs:npc {xyz(SNIPER)} "
    f'{{template:"red_sniper",PersistenceRequired:1b,Tags:["ln","ln_enemy","c1_sniper","ln_dress"],ForgeData:{{ln_side:"red",ln_hunt:64,ln_wp:[I;{SNIPER[0]},{SNIPER[1]},{SNIPER[2]}],ln_wpr:1}}}}',
    "team join ln_red @e[tag=c1_sniper]",
    DRESS_LATER,
    f"bossbar set ln:obj max {FULL}",
    "bossbar set ln:obj color red",
    *radar_wp(),
    "lnhud music @a ch05_battle 40",
    "execute unless score #near_b ln matches 1 run scoreboard players set #near_b ln 0",
    "execute unless score #near_c ln matches 1 run scoreboard players set #near_c ln 0",
])
dialogue("radars")
min_json = jtext([{"text": "艦隊進入射程倒數  ", "color": "red"}, {"score": {"name": "#mm", "objective": "ln"}, "color": "white"},
                  {"text": ":", "color": "white"}, {"score": {"name": "#ss", "objective": "ln"}, "color": "white"},
                  {"text": "　雷達 ", "color": "red"}, {"score": {"name": "#count", "objective": "ln"}, "color": "white"}, {"text": "/3", "color": "white"}])
min_json0 = jtext([{"text": "艦隊進入射程倒數  ", "color": "red"}, {"score": {"name": "#mm", "objective": "ln"}, "color": "white"},
                   {"text": ":0", "color": "white"}, {"score": {"name": "#ss", "objective": "ln"}, "color": "white"},
                   {"text": "　雷達 ", "color": "red"}, {"score": {"name": "#count", "objective": "ln"}, "color": "white"}, {"text": "/3", "color": "white"}])
s4 = [
    f"execute unless score #fail ln matches 1.. run function {NS}/dlg/radars",
    "scoreboard players remove #tl ln 1",
    "execute store result bossbar ln:obj value run scoreboard players get #tl ln",
    "scoreboard players operation #ss ln = #tl ln",
    "scoreboard players operation #ss ln /= #c20 ln",
    "scoreboard players operation #mm ln = #ss ln",
    "scoreboard players set #k ln 60",
    "scoreboard players operation #mm ln /= #k ln",
    "scoreboard players operation #ss ln %= #k ln",
    f"execute if score #ss ln matches 10.. run bossbar set ln:obj name {min_json}",
    f"execute if score #ss ln matches ..9 run bossbar set ln:obj name {min_json0}",
    f"execute if score #tl ln matches {3 * 60 * TPS} run {event('evt_3min')}",
    f"execute if score #tl ln matches ..0 if score #count ln matches ..2 run function {NS}/fail",
    # 敵人
    "execute store result score #alive ln if entity @e[tag=ln_enemy]",
    f"function {NS}/director",
    # 接近台詞
    f"execute if score #near_b ln matches 0 positioned {xyz(A['radar_b'])} if entity {P.replace(']', ',distance=..30]')} run function {NS}/near_b",
    f"execute if score #near_c ln matches 0 positioned {xyz(A['lighthouse_door'])} if entity {P.replace(']', ',distance=..40]')} run function {NS}/near_c",
    # 安裝／倒數／引爆
    *[f"execute as @e[tag=c1_c4{r}] if data entity @s interaction run function {NS}/plant_{r}" for r in RADARS],
    *[f"execute if score #r{r} ln matches 1 run function {NS}/fuse_{r}" for r in RADARS],
    f"execute if score #count ln matches 3.. run scoreboard players add #endt ln 1",
    f"execute if score #endt ln matches 100.. run function {NS}/to_s5",
]
fn("s4", s4)
fn("near_b", ["scoreboard players set #near_b ln 1", event("evt_near_b")])
fn("near_c", ["scoreboard players set #near_c ln 1", event("evt_near_c"), f"schedule function {NS}/sniper_down 100t replace"])
fn("sniper_down", ["execute as @e[tag=c1_sniper] at @s run particle minecraft:crit ~ ~1.6 ~ 0.2 0.2 0.2 0.2 20 force @a",
                   "playsound minecraft:entity.firework_rocket.blast master @a 100 120 1460 4 0.5",
                   "kill @e[tag=c1_sniper]"])
for i, (r, (c4, bx, _)) in enumerate(RADARS.items()):
    fn(f"plant_{r}", [
        "data remove entity @s interaction",
        f"execute if score #r{r} ln matches 0 run function {NS}/plant_{r}_go",
    ])
    fn(f"plant_{r}_go", [
        f"scoreboard players set #r{r} ln 1",
        f"scoreboard players set #f{r} ln 300",
        f"kill @e[tag=c1_lbl{r}]",
        f"playsound minecraft:block.note_block.bit master @a {xyz(c4)} 2 1.6",
        event(f"evt_plant_{r}"),
        *squad(NEAREST[r], goal=(c4[0], c4[1], c4[2]), hunt=48),
        f"summon block_display {c4[0] + 0.3} {c4[1] + 1} {c4[2] + 0.3} " + '{Tags:["ln","c1_c4vis_' + r + '"],block_state:{Name:"minecraft:tnt"},'
        "transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.4f,0.3f,0.4f]},brightness:{sky:15,block:15}}",
    ])
    fn(f"fuse_{r}", [
        f"scoreboard players remove #f{r} ln 1",
        f"scoreboard players operation #fs ln = #f{r} ln",
        "scoreboard players operation #fs ln /= #c20 ln",
        f"scoreboard players operation #fm ln = #f{r} ln",
        "scoreboard players operation #fm ln %= #c20 ln",
        f"execute if score #fm ln matches 0 run playsound minecraft:block.note_block.bit master @a {xyz(c4)} 2 1.9",
        f"execute if score #fm ln matches 0 positioned {xyz(c4)} run title @a[distance=..48] actionbar "
        + jtext([{"text": NAMES[r] + "  C4 引爆倒數 ", "color": "#F0A040"}, {"score": {"name": "#fs", "objective": "ln"}, "color": "white"}, {"text": " 秒", "color": "#F0A040"}]),
        f"particle minecraft:dust 1 0 0 1.2 {c4[0] + 0.5} {c4[1] + 1.2} {c4[2] + 0.5} 0.1 0.1 0.1 0 2 force @a",
        f"execute if score #f{r} ln matches ..0 run function {NS}/boom_{r}",
    ])
    x1, y1, z1, x2, y2, z2 = bx
    extra = []
    if r == "b":
        rb = A["radome_box"]
        extra = [f"fill {rb[0]} {rb[1]} {rb[2]} {rb[3]} {rb[4]} {rb[5]} air", *boom((rb[0] + 3, rb[1] + 2, rb[2] + 3), big=False)]
    fn(f"boom_{r}", [
        f"scoreboard players set #r{r} ln 2",
        f"kill @e[tag=c1_c4{r}]", f"kill @e[tag=c1_c4vis_{r}]", f"kill @e[tag=c1_lbl{r}]",
        *boom(((x1 + x2) // 2, y1 + 4, (z1 + z2) // 2)),
        *boom(((x1 + x2) // 2, y2 - 3, (z1 + z2) // 2), big=False),
        f"fill {x1} {y1} {z1} {x2} {y2} {z2} air",
        *extra,
        # 倒塌殘骸
        f"fill {x1 + 1} {y1} {z1 + 2} {x2 - 2} {y1} {z1 + 3} smooth_quartz_slab",
        f"setblock {x1 + 2} {y1} {z2 - 2} iron_bars",
        f"setblock {x1 + 3} {y1} {z2 - 3} campfire[lit=true]",
        f"setblock {(x1 + x2) // 2} {y1} {(z1 + z2) // 2} campfire[lit=true]",
        f"execute positioned {(x1 + x2) // 2} {y1} {(z1 + z2) // 2} run kill @e[tag=ln_enemy,distance=..6]",
        "lnhud tint @a 70FFE0B0 20 flash",
        "scoreboard players add #count ln 1",
        event(f"evt_boom_{r}"),
        f"execute if score #count ln matches 1 run {event('evt_count_1')}",
        f"execute if score #count ln matches 2 run {event('evt_count_2')}",
        f"execute if score #count ln matches 3 run {event('evt_count_3')}",
        *radar_wp(),
    ])
fn("fail", [
    "scoreboard players add #fail ln 1",
    event("evt_fail"),
    "kill @e[tag=ln_enemy]",
    f"scoreboard players set #tl ln {RETRY}",
    *[f"execute if score #r{r} ln matches 1 run kill @e[tag=c1_c4vis_{r}]" for r in RADARS],
    f"function {NS}/arm",
    "scoreboard players set #dt ln 0",
])

# ---- 5 撤離：艦隊打擊 → 山體異變 → 守夜人 → 懸崖觀測站
STRIKES = [(22, 1300), (30, 1330), (12, 1340), (40, 1290), (18, 1318), (36, 1350), (50, 1372), (8, 1310), (28, 1280), (60, 1400),
           (66, 1430), (98, 1450), (44, 1386), (14, 1296), (34, 1312)]
OBS = A["observation_post"]
CRACK = A["mountain_crack"]
fn("to_s5", [
    *goto(5),
    "scoreboard players set #endt ln 0",
    *bossbar("目標：撤到北邊的懸崖觀測站", "green"),
    "bossbar set ln:obj max 1", "bossbar set ln:obj value 1",
    "lnhud music @a ch05_suspense 80",
])
end5 = dialogue("strike")
s5 = [f"function {NS}/dlg/strike"]
for i, (x, z) in enumerate(STRIKES):
    t = 70 + i * 12
    y = surf(x, z)
    s5.append(f"execute if score #t ln matches {t} positioned {x} {y} {z} unless entity @a[distance=..10] run function {NS}/strike_fx")
s5 += [
    f"execute if score #t ln matches 60 as @a at @s run playsound minecraft:entity.firework_rocket.launch master @s ~40 ~30 ~ 4 0.5",
    "execute if score #t ln matches 130 run kill @e[tag=ln_enemy]",
    f"execute if score #t ln matches 120 run lnhud waypoint @a {xyz(OBS)}",
    # 山體異變：低頻震動、嗡鳴、裂縫一瞬間的藍光（看不到巨砲本體）
    "scoreboard players operation #tm ln = #t ln",
    "scoreboard players set #k ln 30",
    "scoreboard players operation #tm ln %= #k ln",
    "execute if score #t ln matches 300..900 if score #tm ln matches 0 as @a at @s run playsound minecraft:entity.warden.heartbeat master @s ~ ~-6 ~ 2 0.5",
    "execute if score #t ln matches 340..900 if score #tm ln matches 15 as @a at @s run playsound minecraft:block.beacon.ambient master @s ~ ~ ~ 1.5 0.5",
    "execute if score #t ln matches 330..900 as @a at @s run particle minecraft:ash ~ ~1 ~ 6 2 6 0 4 normal @s",
    f"execute if score #t ln matches 420 run summon block_display {CRACK[0]} {CRACK[1]} {CRACK[2]} "
    '{Tags:["ln","c1_glow"],brightness:{sky:15,block:15},block_state:{Name:"minecraft:light_blue_stained_glass"},Glowing:1b,glow_color_override:6737151,'
    "transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[-1f,-6f,-3f],scale:[2f,12f,6f]}}",
    f"execute if score #t ln matches 420 run particle minecraft:electric_spark {xyz(CRACK)} 2 6 3 0.4 200 force @a",
    "execute if score #t ln matches 420 run lnhud tint @a 8060C0FF 30 flash",
    "execute if score #t ln matches 450 run kill @e[tag=c1_glow]",
    "execute if score #t ln matches 600 as @a at @s run playsound lnai:sfx.radio_off master @s ~ ~ ~ 1 0.8",
    "execute if score #t ln matches 735 as @a at @s run playsound lnai:sfx.radio_on master @s ~ ~ ~ 1 0.7",
    # 抵達觀測站（台詞播完後才結束）
    f"execute if score #t ln matches {end5}.. positioned {xyz(OBS)} if entity {P.replace(']', ',distance=..7]')} run function {NS}/arrive",
]
fn("s5", s5)
fn("strike_fx", [*boom(("~", "~1", "~")), "particle minecraft:flash ~ ~2 ~ 0 0 0 0 1 force @a",
                 "execute as @a[distance=..40] run lnhud tint @s 50FFD0A0 14 flash"])
fn("arrive", [*goto(6), event("arrive"), f"schedule function {NS}/finish 60t replace"])
fn("finish", [
    "scoreboard players set #stage ln 0",
    "scoreboard players set #done1 ln 1",
    "bossbar set ln:obj visible false",
    "lnhud objective @a",
    "lnhud waypoint @a clear",
    "lnhud title @a 100 FFFFB020 第一章　雷霆空降|任務完成・返回運輸機",
    "lnhud music @a ch05_after 60",
    f"schedule function {NS}/to_lobby 140t replace",
])
fn("to_lobby", [
    "lnglass restore",
    "scoreboard players set #run ln 0",
    "lnhud tint @a FF000000 40",
    "lnhud music @a stop 50",
    "schedule function ln:lobby/enter 50t replace",
])
# 全隊倒地：清敵人，從目前階段開頭重來（雷達階段倒數不重設，但至少留 3 分鐘）
REFILL = [f"clear {P}", f"function {NS}/loadout", f"effect give {P} instant_health 1 9 true",
          f"tellraw @a {jtext({'text': '[長夜] 補給已重新發放。', 'color': 'gray'})}"]
fn("wipe", [
    "kill @e[tag=ln_enemy]",
    *REFILL,
    f"execute if score #stage ln matches 2 run tp {P} {xyz(A['path_bottom'])}",
    f"execute if score #stage ln matches 2 run function {NS}/to_s2",
    f"execute if score #stage ln matches 3 run tp {P} {PANEL[0]} {PANEL[1] - 1} {PANEL[2] + 4}",
    f"execute if score #stage ln matches 3 run function {NS}/to_s3",
    f"execute if score #stage ln matches 4 run tp {P} {PANEL[0]} {PANEL[1] - 1} {PANEL[2] - 4}",
    f"execute if score #stage ln matches 4 if score #tl ln matches ..{3 * 60 * TPS} run scoreboard players set #tl ln {3 * 60 * TPS}",
    f"execute if score #stage ln matches 4 run function {NS}/to_s4",
])
fn("tick", [
    "scoreboard players add #t ln 1",
    *[f"execute if score #stage ln matches {i} run function {NS}/s{i}" for i in (1, 2, 3, 4, 5)],
])
# 雷達階段第一次進入時才設定 12 分鐘；失敗重來時不會再被蓋掉
files["to_s4"] = files["to_s4"].replace(
    "execute unless score #count ln matches 0.. run scoreboard players set #count ln 0",
    "execute unless score #count ln matches 0.. run scoreboard players set #count ln 0\n"
    f"execute unless score #tl ln matches 1.. run scoreboard players set #tl ln {FULL}")
files["start"] = files["start"].replace("scoreboard players set #run ln 1",
                                        "scoreboard players set #run ln 1\nscoreboard players reset #count ln\nscoreboard players reset #tl ln\n"
                                        "scoreboard players set #fail ln 0\nscoreboard players set #endt ln 0\n"
                                        "scoreboard players reset #near_b ln\nscoreboard players reset #near_c ln\n"
                                        "scoreboard players reset #ra ln\nscoreboard players reset #rb ln\nscoreboard players reset #rc ln")

# ================================================================== 寫檔
if OUT.exists():
    shutil.rmtree(OUT)
for name, body in files.items():
    p = OUT / f"{name}.mcfunction"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
print(f"已產生 {len(files)} 個函式到 {OUT.relative_to(ROOT)}")
