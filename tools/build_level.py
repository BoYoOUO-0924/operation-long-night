"""把關卡設定（levels/*.json + 建築錨點 + 地形高度）編譯成資料包函式。

執行：python tools/build_level.py
產生：datapack/longnight/data/ln/functions/ch05/**（請勿手動修改這些檔案）

階段（#stage ln）：
  1 approach 上山（隊友跟隨玩家）  2 arrival 抵達  3 reveal 揭露  4 prepare 準備防守
  5 combat 小隊戰（導演系統持續派兵）  7 outro 收尾  0 未進行

敵人 AI 由 lnai 模組執行，資料包只透過 ForgeData 下命令：
  ln_side 陣營、ln_squad 小隊、ln_wp 目標點、ln_hunt 主動搜索半徑、ln_follow 跟隨玩家
"""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACK = ROOT / "datapack/longnight/data/ln/functions"
OUT = PACK / "ch05"
A = json.loads((ROOT / "generators/out/weather_station.json").read_text(encoding="utf-8"))
L = json.loads((ROOT / "levels/ch05_trial.json").read_text(encoding="utf-8"))
HM = json.loads((ROOT / "generators/out/heightmap_ch05.json").read_text(encoding="utf-8"))
SPK = L["speakers"]
TPS = 20

files = {}


def fn(name, lines):
    files[name] = "# 由 tools/build_level.py 自動產生，請勿手動修改\n" + "\n".join(lines) + "\n"


def xyz(p):
    return f"{p[0]} {p[1]} {p[2]}"


FONT = "lnai:ui"   # lnai 模組內建的戰術字型（數字 Rajdhani、中文思源黑體）


def jtext(obj):
    if isinstance(obj, list):
        obj = {"text": "", "font": FONT, "extra": obj}
    elif isinstance(obj, dict) and "font" not in obj:
        obj = {**obj, "font": FONT}
    return json.dumps(obj, ensure_ascii=False)


def surf(x, z):
    """(x,z) 的站立高度。"""
    t = HM["top"][z - HM["z1"]][x - HM["x1"]]
    s = HM["solid"][z - HM["z1"]][x - HM["x1"]]
    return t if t != s else t + 1


def say_line(who, text):
    color = SPK.get(who, "white")
    if who == "目標":
        return [f"tellraw @a {jtext([{'text': '▶ 目標：', 'color': color, 'bold': True}, {'text': text, 'color': 'white'}])}",
                f"lnhud objective @a {text}",
                "execute as @a at @s run playsound minecraft:block.note_block.bell master @s ~ ~ ~ 0.6 1.2"]
    if who == "提示":
        return [f"tellraw @a {jtext([{'text': '（提示）', 'color': color}, {'text': text, 'color': 'gray', 'italic': True}])}"]
    sound = ("minecraft:block.note_block.basedrum master @s ~ ~ ~ 0.8 0.5" if who == "守夜人"
             else "minecraft:ui.button.click master @s ~ ~ ~ 0.3 1.8")
    return [f"tellraw @a {jtext([{'text': f'[{who}] ', 'color': color, 'bold': True}, {'text': text, 'color': 'white'}])}",
            f"execute as @a at @s run playsound {sound}"]


OBJ_WP = {  # 對白段落 → 目標導航點（None = 清除）
    "approach": "garage_door_outside", "arrival": "parts_button", "generator_fail": "generator_lever",
    "prepare": None, "final_assault": None, "generator_fixed": None,
}


def obj_wp(key):
    if key not in OBJ_WP:
        return []
    a = OBJ_WP[key]
    return [f"lnhud waypoint @a {xyz(A[a])}" if a else "lnhud waypoint @a clear"]


def dialogue(key):
    """跟著階段計時器（#t）播放的對白。"""
    lines = []
    for d in L["dialogue"][key]:
        t = int(d["at"] * TPS)
        for cmd in say_line(d["who"], d["text"]) + (obj_wp(key) if d["who"] == "目標" else []):
            lines.append(f"execute if score #t ln matches {t} run {cmd}")
    fn(f"dlg/{key}", lines)
    return int(max(d["at"] for d in L["dialogue"][key]) * TPS)


def event_dialogue(key):
    """事件對白：立刻播第一句，其餘用 schedule 排程。回傳啟動函式名稱。"""
    lines = L["dialogue"][key]
    start = []
    for i, d in enumerate(lines):
        name = f"evdlg/{key}_{i}"
        fn(name, say_line(d["who"], d["text"]) + (obj_wp(key) if d["who"] == "目標" else []))
        t = int(d["at"] * TPS)
        start.append(f"function ln:ch05/{name}" if t == 0 else f"schedule function ln:ch05/{name} {t}t append")
    fn(f"evdlg/{key}", start)
    return f"function ln:ch05/evdlg/{key}"


def bossbar(name, color="yellow"):
    return [f"bossbar set ln:obj name {jtext({'text': name})}", f"bossbar set ln:obj color {color}"]


def goto(stage):
    return [f"scoreboard players set #stage ln {stage}", "scoreboard players set #t ln 0"]


def wp(p, r=3, hunt=None, extra=""):
    h = f",ln_hunt:{hunt}" if hunt is not None else ""
    return f"{{ForgeData:{{ln_wp:[I;{p[0]},{p[1]},{p[2]}],ln_wpr:{r}{h}{extra}}}}}"


# ================================================================== 裝備外觀（ZeroContact 頭盔／防彈衣）
GEAR = {  # 選擇器條件 → (頭盔, 防彈衣)
    "tag=ln_baiya": ("helmet_tbh_iiia", "armor_jpc_v1"),
    "tag=ln_tank": ("helmet_bastion_black", "armor_6b43"),
    "tag=ln_fox": ("helmet_phonetalker_iiia", "armor_avs"),
    'nbt={template:"red_assault"}': ("helmet_6b47_ratnik_arc", "armor_6b23_1"),
    'nbt={template:"red_support"}': ("helmet_6b47_ratnik_emr", "armor_6b23_2"),
    'nbt={template:"red_sniper"}': ("cap_boss", "armor_6b2"),
    'nbt={template:"red_cqb"}': ("helmet_bastion_green", "armor_thor_black"),
}
PLAYER_GEAR = ("helmet_airframe", "armor_defender_2")
dress = []
for sel, (helm, vest) in GEAR.items():
    dress += [f"item replace entity @e[tag=ln_dress,{sel}] armor.head with zerocontact:{helm}",
              f"item replace entity @e[tag=ln_dress,{sel}] armor.chest with zerocontact:{vest}"]
fn("dress", dress + ["tag @e[tag=ln_dress] remove ln_dress"])
DRESS_LATER = "schedule function ln:ch05/dress 2t replace"

# ================================================================== 隊友
ALLIES = [  # tag, 名字, 顏色, 模板, 跟隨站位
    ("ln_baiya", "白鴉", "aqua", "blue_sniper", 1),
    ("ln_tank", "戰車", "gold", "blue_support", 2),
    ("ln_fox", "狐狸", "green", "blue_assault", 3),
    ("ln_officer", "情報官", "gray", "ln_officer", 4),
]


def summon_ally(tag, name, color, template, slot, pos):
    hunt = "" if tag == "ln_officer" else ",ln_hunt:24"
    nbt = (f'{{template:"{template}",CustomName:\'{jtext({"text": name, "color": color})}\',CustomNameVisible:1b,'
           f'Invulnerable:1b,PersistenceRequired:1b,Tags:["ln","ln_ally","{tag}","ln_new","ln_dress"],'
           f'ForgeData:{{ln_side:"blue",ln_follow:1b,ln_slot:{slot}{hunt}}}}}')
    return f"summon tacznpcs:npc {pos} {nbt}"


sx, sz = A["start_center"]
fn("spawn_allies_start", [summon_ally(*a, pos=f"{sx} 250 {sz}") for a in ALLIES] + [
    f"spreadplayers {sx} {sz} 2 5 false @e[tag=ln_new]",
    "team join ln_blue @e[tag=ln_new]",
    "effect give @e[tag=ln_new,tag=!ln_officer] glowing infinite 0 true",
    "tag @e[tag=ln_new] remove ln_new",
    DRESS_LATER,
])

# ================================================================== 進攻路線（出生 → 集結 → 突擊）
cx, cy, cz = A["center"]
ROUTES = {
    "east":      {"spawn": (172, 962), "approach": (150, 962), "assault": (132, 136, 961)},
    "north":     {"spawn": (104, 918), "approach": (100, 940), "assault": (82, 136, 960)},
    "south":     {"spawn": (100, 1018), "approach": (102, 996), "assault": (102, 136, 978)},
    "west":      {"spawn": (54, 966), "approach": (68, 965), "assault": (82, 136, 966)},
    "northeast": {"spawn": (150, 928), "approach": (136, 944), "assault": (131, 136, 957)},
}
for r in ROUTES.values():
    ax, az = r["approach"]
    r["approach"] = (ax, surf(ax, az), az)
ORDER = ["east", "north", "south", "east", "west", "northeast"]   # 輪流派兵的順序

COMPS = [  # 小隊編成（第 4 人在 3 人以上時加入）
    ["red_assault", "red_assault", "red_support", "red_assault"],
    ["red_assault", "red_cqb", "red_cqb", "red_support"],
    ["red_assault", "red_sniper", "red_support", "red_assault"],
]


def enemy_nbt(route, template, slot):
    return (f'{{template:"{template}",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_{route}"],'
            f'ForgeData:{{ln_side:"red",ln_slot:{slot},ln_hunt:16}}}}')


callouts = L["callouts"]
callout_spk = L["callout_speakers"]
for route, r in ROUTES.items():
    x, z = r["spawn"]
    lines = []
    for ci, comp in enumerate(COMPS):
        for slot, tpl in enumerate(comp[:3]):
            lines.append(f"execute if score #comp ln matches {ci} run summon tacznpcs:npc {x} 250 {z} {enemy_nbt(route, tpl, slot)}")
        lines.append(f"execute if score #comp ln matches {ci} if score #players ln matches 3.. run "
                     f"summon tacznpcs:npc {x} 250 {z} {enemy_nbt(route, comp[3], 3)}")
    lines += [f"spreadplayers {x} {z} 1 6 false @e[tag=ln_new]", DRESS_LATER]
    for i, text in enumerate(callouts[route]):
        for cmd in say_line(callout_spk[route], text):
            lines.append(f"execute if score #flip ln matches {i} run {cmd}")
    fn(f"dir/route_{route}", lines)

# 小隊命名（1.20.1 沒有巨集，用 8 個固定名稱輪流）
for k in range(8):
    fn(f"dir/name_{k}", [f'execute as @e[tag=ln_new] run data merge entity @s {{ForgeData:{{ln_squad:"s{k}"}}}}'])

spawn_next = [
    "scoreboard players add #sq ln 1",
    "scoreboard players operation #slot ln = #sq ln",
    "scoreboard players operation #slot ln %= #c8 ln",
    "scoreboard players operation #comp ln = #sq ln",
    "scoreboard players operation #comp ln %= #c3 ln",
    "scoreboard players operation #flip ln = #sq ln",
    "scoreboard players operation #flip ln %= #c2 ln",
    *[f"execute if score #route ln matches {i} run function ln:ch05/dir/route_{name}" for i, name in enumerate(ORDER)],
    *[f"execute if score #slot ln matches {k} run function ln:ch05/dir/name_{k}" for k in range(8)],
    "team join ln_red @e[tag=ln_new]",
    "execute store result score #n ln if entity @e[tag=ln_new]",
    "scoreboard players operation #budget ln -= #n ln",
    "tag @e[tag=ln_new] remove ln_new",
    "scoreboard players add #route ln 1",
    f"execute if score #route ln matches {len(ORDER)}.. run scoreboard players set #route ln 0",
    "scoreboard players set #dt ln 0",
]
fn("dir/spawn_next", spawn_next)
fn("dir/spawn_route", [])  # 保留


def force_route(name):
    i = ORDER.index(name)
    return [f"scoreboard players set #route ln {i}", "function ln:ch05/dir/spawn_next"]


# 依年齡推進：集結 → 突擊 → 全面搜索
phase = []
for route, r in ROUTES.items():
    phase.append(f"execute as @e[tag=ln_enemy,tag=rt_{route},scores={{ln_age=2}}] run data merge entity @s {wp(r['approach'], 3, 20)}")
    phase.append(f"execute as @e[tag=ln_enemy,tag=rt_{route},scores={{ln_age=220}}] run data merge entity @s {wp(r['assault'], 3, 40)}")
phase += [
    "execute as @e[tag=ln_enemy,scores={ln_age=700}] run data merge entity @s {ForgeData:{ln_hunt:96}}",
    "execute as @e[tag=ln_enemy,scores={ln_age=1800}] run effect give @s glowing 600 0 true",
    "execute as @e[tag=ln_enemy,scores={ln_age=5000}] run kill @s",
]
fn("dir/phase", phase)

# ================================================================== 狐狸的掃描器
SECTORS = {  # 名稱：volume（相對中心）
    "北": (cx - 90, cz - 90, 180, 74),
    "南": (cx - 90, cz + 16, 180, 74),
    "東": (cx + 24, cz - 16, 70, 32),
    "西": (cx - 90, cz - 16, 66, 32),
}
pulse = [
    f"execute positioned {cx} {cy} {cz} run effect give @e[tag=ln_enemy,distance=..90] glowing 3 0 true",
    f"execute as @a at @s run playsound minecraft:block.beacon.power_select master @s ~ ~ ~ 0.5 1.8",
]
parts = [{"text": "[狐狸] ", "color": "green", "bold": True}, {"text": "掃描：", "color": "white"}]
for i, (name, (x0, z0, dx, dz)) in enumerate(SECTORS.items()):
    pulse.append(f"execute store result score #q{i} ln if entity @e[tag=ln_enemy,x={x0},y=60,z={z0},dx={dx},dy=160,dz={dz}]")
    parts += [{"text": f"{name} ", "color": "gray"}, {"score": {"name": f"#q{i}", "objective": "ln"}, "color": "yellow"},
              {"text": "　", "color": "gray"}]
pulse.append(f"execute if entity @e[tag=ln_enemy] run tellraw @a {jtext(parts)}")
fn("dir/pulse", pulse)

# ================================================================== 事件：發電機故障
lever = xyz(A["generator_lever"])
lx, ly, lz = A["generator_lever"]
fn("ev/gen_fail", [
    "scoreboard players set #evgen ln 1",
    "scoreboard players set #gent ln 0",
    f"setblock {lever} lever[face=floor,facing=north,powered=false]",
    event_dialogue("generator_fail"),
    *force_route("south"),
])
fn("ev/gen_tick", [
    "scoreboard players add #gent ln 1",
    f"particle minecraft:campfire_signal_smoke {lx} {ly + 1} {lz} 0.2 0.5 0.2 0.01 2 force @a",
    f"execute if score #gent ln matches 1200.. run scoreboard players operation #gm ln = #gent ln",
    f"execute if score #gent ln matches 1200.. run scoreboard players operation #gm ln %= #c100 ln",
    "execute if score #gent ln matches 1200.. if score #gm ln matches 0 run effect give @a[gamemode=adventure] slowness 6 0 true",
    "execute if score #gent ln matches 1200.. if score #gm ln matches 0 run effect give @a[gamemode=adventure] mining_fatigue 6 0 true",
    f"execute if score #gent ln matches 1200 run {event_dialogue('generator_cold')}",
    f"execute if block {lever} lever[powered=true] run function ln:ch05/ev/gen_fixed",
])
fn("ev/gen_fixed", [
    "scoreboard players set #evgen ln 2",
    "effect clear @a slowness",
    "effect clear @a mining_fatigue",
    "function ln:ch05/ammo",
    event_dialogue("generator_fixed"),
])

# ================================================================== 事件：主攻（武裝皮卡 + 迫擊砲）
ex = ROUTES["east"]
PATH = [(x, surf(x, 962), 962) for x in range(164, 139, -4)]
tech_spawn = PATH[0]
fn("ev/final", [
    "scoreboard players set #final ln 1",
    event_dialogue("final_assault"),
    *force_route("east"),
    *force_route("north"),
    f'summon superbwarfare:sodayo_pick_up_hmg {tech_spawn[0]} {tech_spawn[1]} {tech_spawn[2]} {{Rotation:[90f,0f],Tags:["ln","ln_tech"]}}',
    f'summon tacznpcs:npc {tech_spawn[0]} {tech_spawn[1] + 2} {tech_spawn[2]} {{template:"red_support",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_techgun","ln_dress"],ForgeData:{{ln_side:"red",ln_hunt:64}}}}',
    f'summon tacznpcs:npc {tech_spawn[0]} {tech_spawn[1] + 2} {tech_spawn[2]} {{template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_techgun","ln_dress"],ForgeData:{{ln_side:"red",ln_hunt:64}}}}',
    "execute as @e[tag=ln_techgun] run ride @s mount @e[tag=ln_tech,limit=1]",
    "team join ln_red @e[tag=ln_techgun]",
    "scoreboard players set #tp ln 1",
    "scoreboard players set #tpt ln 0",
    "scoreboard players set #mort ln 6",
    "scoreboard players set #mt ln 0",
])
drive = []
for i, (x, y, z) in enumerate(PATH[1:], start=1):
    drive.append(f"execute if score #tp ln matches {i} as @e[tag=ln_tech] at @s facing {x} {y + 0.2} {z} run tp @s ^ ^ ^0.3")
    drive.append(f"execute if score #tp ln matches {i} as @e[tag=ln_tech] at @s positioned {x} {y} {z} if entity @s[distance=..1.5] run scoreboard players add #tp ln 1")
drive += [
    "scoreboard players add #tpt ln 1",
    f"execute if score #tp ln matches {len(PATH)}.. run function ln:ch05/ev/tech_arrive",
    "execute if score #tpt ln matches 400.. run function ln:ch05/ev/tech_arrive",
]
fn("ev/drive", drive)
fn("ev/tech_arrive", [
    "scoreboard players set #tp ln 0",
    "execute as @e[tag=ln_techgun] run ride @s dismount",
    f"execute as @e[tag=ln_techgun] run data merge entity @s {wp(ROUTES['east']['assault'], 3, 64)}",
    f"tellraw @a {jtext([{'text': '[白鴉] ', 'color': 'aqua', 'bold': True}, {'text': '皮卡停了，槍手下車了！東邊車庫外！', 'color': 'white'}])}",
])

fn("ev/mortar_tick", [
    "scoreboard players add #mt ln 1",
    "execute if score #mt ln matches 80 if score #mort ln matches 1.. as @r[gamemode=adventure] at @s run summon marker ~ ~ ~ {Tags:[\"ln\",\"ln_mortar\",\"ln_newm\"]}",
    "execute as @e[tag=ln_newm] at @s run spreadplayers ~ ~ 0 8 false @s",
    "tag @e[tag=ln_newm] remove ln_newm",
    "execute if score #mt ln matches 80 if score #mort ln matches 1.. run scoreboard players remove #mort ln 1",
    "execute if score #mt ln matches 80 run scoreboard players set #mt ln 0",
    "scoreboard players add @e[tag=ln_mortar] ln_age 1",
    "execute as @e[tag=ln_mortar] at @s run particle minecraft:dust 1 0 0 2 ~ ~0.2 ~ 1.5 0 1.5 0 6 force @a",
    "execute as @e[tag=ln_mortar,scores={ln_age=10}] at @s run playsound minecraft:entity.firework_rocket.launch master @a ~ ~ ~ 2 0.5",
    "execute as @e[tag=ln_mortar,scores={ln_age=30}] at @s run playsound minecraft:entity.arrow.shoot master @a ~ ~20 ~ 2 0.3",
    'execute as @e[tag=ln_mortar,scores={ln_age=50}] at @s run summon superbwarfare:mortar_shell ~ ~40 ~ {Motion:[0.0d,-2.0d,0.0d]}',
    "kill @e[tag=ln_mortar,scores={ln_age=50..}]",
])

# ================================================================== 裝備
fn("ammo", [
    'give @a[gamemode=adventure] tacz:ammo{AmmoId:"tacz:556x45"} 120',
    'give @a[gamemode=adventure] tacz:ammo{AmmoId:"tacz:9mm"} 34',
])
# 快捷欄固定：1 主武器、2 副武器、3 近戰（空）、4 投擲物、5 醫療；其餘放背包，由 lnai 模組按 4／5 時換上來
P = "@a[gamemode=adventure]"
fn("loadout", [
    f'item replace entity {P} hotbar.0 with tacz:modern_kinetic_gun{{GunId:"tacz:m4a1",GunCurrentAmmoCount:30,HasBulletInBarrel:1b}}',
    f'item replace entity {P} hotbar.1 with tacz:modern_kinetic_gun{{GunId:"tacz:glock_17",GunCurrentAmmoCount:17,HasBulletInBarrel:1b}}',
    f"item replace entity {P} hotbar.3 with superbwarfare:hand_grenade 2",
    f"item replace entity {P} hotbar.4 with lnai:bandage 4",
    "function ln:ch05/ammo",
    f"give {P} lnai:painkiller 2",
    f"give {P} lnai:medkit 2",
    f"give {P} superbwarfare:rgo_grenade 1",
    f"give {P} superbwarfare:m18_smoke_grenade 1",
    f"item replace entity {P} armor.head with zerocontact:{PLAYER_GEAR[0]}",
    f"item replace entity {P} armor.chest with zerocontact:{PLAYER_GEAR[1]}",
    f"effect give {P} saturation infinite 0 true",
])

# ================================================================== 流程
fn("cleanup", [
    "kill @e[tag=ln]",
    "scoreboard players set #stage ln 0",
    "bossbar set ln:obj visible false",
    "effect clear @a",
    "schedule clear ln:ch05/evdlg/generator_fail_1",
    "lnhud objective @a",
    "gamerule naturalRegeneration true",
])
fn("start", [
    "function ln:ch05/cleanup",
    "forceload add 50 900 240 1020",
    "function ln:build/station_place",
    "kill @e[type=item]",
    "time set 18000",
    "weather thunder 1000000",
    "scoreboard players set #c2 ln 2",
    "scoreboard players set #c3 ln 3",
    "scoreboard players set #c8 ln 8",
    "scoreboard players set #c100 ln 100",
    "gamemode adventure @a",
    "gamerule naturalRegeneration false",
    "team join ln_blue @a",
    "clear @a",
    f"spreadplayers {sx} {sz} 0 3 false @a",
    "execute as @a at @s run spawnpoint @s ~ ~ ~",
    "function ln:ch05/loadout",
    "function ln:ch05/spawn_allies_start",
    "bossbar set ln:obj players @a",
    "bossbar set ln:obj visible true",
    "bossbar set ln:obj max 1",
    "bossbar set ln:obj value 1",
    *bossbar("目標：前往山上的氣象站"),
    "title @a times 20 80 20",
    f"title @a subtitle {jtext({'text': '零下四十度', 'color': 'gray'})}",
    f"title @a title {jtext({'text': '第五章　寒霜陷阱', 'color': 'white', 'bold': True})}",
    *goto(1),
])
fn("stop", ["function ln:ch05/cleanup", "gamemode creative @a",
            f"tellraw @a {jtext({'text': '[長夜] 已中止關卡。', 'color': 'red'})}"])

# 1 上山（隊友跟著玩家走）
dialogue("approach")
fn("s1", [
    "function ln:ch05/dlg/approach",
    "effect give @a[gamemode=adventure] slowness 2 0 true",
    "execute at @a run particle minecraft:snowflake ~ ~2 ~ 6 2 6 0.02 25 normal @a",
    f"execute positioned {xyz(A['garage_door_outside'])} if entity @a[gamemode=adventure,distance=..9] run function ln:ch05/to_s2",
])
fn("to_s2", [
    *goto(2),
    "execute as @e[tag=ln_ally] run data merge entity @s {ForgeData:{ln_follow:0b}}",
    f"tp @e[tag=ln_fox] {xyz(A['fox_bench'])}",
    f"tp @e[tag=ln_tank] {xyz(A['tank_radio'])}",
    f"tp @e[tag=ln_officer] {xyz(A['officer_radio'])}",
    f"tp @e[tag=ln_baiya] {xyz(A['baiya_tower'])}",
    "data merge entity @e[tag=ln_officer,limit=1] {NoAI:1b}",
    f"spawnpoint @a {xyz(A['checkpoint'])}",
    "effect clear @a slowness",
    *bossbar("目標：在車庫找到零件箱"),
])
# 2 抵達：按零件箱按鈕
dialogue("arrival")
btn = xyz(A["parts_button"])
fn("s2", [
    "function ln:ch05/dlg/arrival",
    f"execute if score #t ln matches 600.. run particle minecraft:happy_villager {btn} 0.3 0.3 0.3 0 2 force @a",
    f"execute if score #t ln matches 40.. if block {btn} minecraft:stone_button[powered=true] run function ln:ch05/to_s3",
])
fn("to_s3", [
    *goto(3),
    *bossbar("（劇情）狐狸正在修理掃描器"),
    f"execute positioned {xyz(A['fox_bench'])} run playsound minecraft:block.beacon.activate master @a ~ ~ ~ 1 1.5",
])
# 3 揭露
end3 = dialogue("reveal") + 4 * TPS
fn("s3", [
    "function ln:ch05/dlg/reveal",
    "execute if score #t ln matches 180 run effect give @e[tag=ln_officer] glowing 12 0 true",
    "execute if score #t ln matches 180 as @a at @s run playsound minecraft:block.note_block.pling master @s ~ ~ ~ 1 2",
    f"execute if score #t ln matches {end3} run function ln:ch05/to_s4",
])
# 4 準備：隊友就防守位置
fn("to_s4", [
    *goto(4), "function ln:ch05/ammo", "give @a[gamemode=adventure] lnai:bandage 2", "give @a[gamemode=adventure] lnai:medkit 1", "give @a[gamemode=adventure] superbwarfare:hand_grenade 1", *bossbar("準備防守：敵軍即將抵達", "red"),
    "bossbar set ln:obj max 400",
    "execute as @e[tag=ln_tank] run data merge entity @s {ForgeData:{ln_follow:1b,ln_hunt:40}}",
    "execute as @e[tag=ln_fox] run data merge entity @s {ForgeData:{ln_follow:1b,ln_hunt:40}}",
    f"tellraw @a {jtext([{'text': '[戰車] ', 'color': 'gold', 'bold': True}, {'text': '我和狐狸跟著你，你往哪打我們就往哪打。白鴉在塔上掩護。', 'color': 'white'}])}",
    f"data merge entity @e[tag=ln_baiya,limit=1] {wp(A['baiya_tower'], 1, 64)}",
])
dialogue("prepare")
fn("s4", [
    "function ln:ch05/dlg/prepare",
    "execute store result bossbar ln:obj value run scoreboard players get #t ln",
    "execute if score #t ln matches 400 run function ln:ch05/to_s5",
])
# 5 小隊戰
dialogue("combat_start")
fn("to_s5", [
    *goto(5),
    "execute store result score #players ln if entity @a[gamemode=adventure]",
    "execute if score #players ln matches ..0 run scoreboard players set #players ln 1",
    # 兵力：1 人 40，每多 1 人 +14；同時在場上限：10，每多 1 人 +3
    "scoreboard players operation #budget ln = #players ln",
    "scoreboard players remove #budget ln 1",
    "scoreboard players operation #max ln = #budget ln",
    "scoreboard players set #k ln 14",
    "scoreboard players operation #budget ln *= #k ln",
    "scoreboard players add #budget ln 40",
    "scoreboard players set #k ln 3",
    "scoreboard players operation #max ln *= #k ln",
    "scoreboard players add #max ln 10",
    "scoreboard players operation #total ln = #budget ln",
    "scoreboard players set #sq ln 0",
    "scoreboard players set #route ln 0",
    "scoreboard players set #dt ln 400",
    "scoreboard players set #pulse ln 0",
    "scoreboard players set #evgen ln 0",
    "scoreboard players set #final ln 0",
    "scoreboard players set #tp ln 0",
    "scoreboard players set #mort ln 0",
    "execute store result bossbar ln:obj max run scoreboard players get #total ln",
    "bossbar set ln:obj color red",
])
name_json = jtext([{"text": "敵軍剩餘兵力：", "color": "red"}, {"score": {"name": "#left", "objective": "ln"}, "color": "white"},
                   {"text": "　場上：", "color": "red"}, {"score": {"name": "#alive", "objective": "ln"}, "color": "white"}])
fn("s5", [
    "function ln:ch05/dlg/combat_start",
    "scoreboard players add @e[tag=ln_enemy] ln_age 1",
    "function ln:ch05/dir/phase",
    "execute store result score #alive ln if entity @e[tag=ln_enemy]",
    "scoreboard players operation #left ln = #budget ln",
    "scoreboard players operation #left ln += #alive ln",
    "execute store result bossbar ln:obj value run scoreboard players get #left ln",
    f"bossbar set ln:obj name {name_json}",
    # 導演：每 15 秒派一組；場上少於 4 人時 6 秒就補
    "scoreboard players add #dt ln 1",
    "execute if score #final ln matches 0 if score #budget ln matches 7.. if score #dt ln matches 300.. if score #alive ln < #max ln run function ln:ch05/dir/spawn_next",
    "execute if score #final ln matches 1 if score #budget ln matches 1.. if score #dt ln matches 300.. if score #alive ln < #max ln run function ln:ch05/dir/spawn_next",
    "execute if score #budget ln matches 7.. if score #dt ln matches 120.. if score #alive ln matches ..3 run function ln:ch05/dir/spawn_next",
    "execute if score #final ln matches 0 if score #budget ln matches ..6 if score #alive ln matches 0 run function ln:ch05/ev/final",
    # 掃描器每 15 秒
    "scoreboard players add #pulse ln 1",
    "execute if score #pulse ln matches 300.. run function ln:ch05/dir/pulse",
    "execute if score #pulse ln matches 300.. run scoreboard players set #pulse ln 0",
    # 事件：剩 55% 發電機故障；剩 25% 主攻
    # 擊殺進度 = (總兵力 - 未派出 - 場上) / 總兵力
    "scoreboard players operation #pct ln = #total ln",
    "scoreboard players operation #pct ln -= #left ln",
    "scoreboard players set #k ln 100",
    "scoreboard players operation #pct ln *= #k ln",
    "scoreboard players operation #pct ln /= #total ln",
    "execute if score #evgen ln matches 0 if score #pct ln matches 35.. run function ln:ch05/ev/gen_fail",
    "execute if score #evgen ln matches 1 run function ln:ch05/ev/gen_tick",
    "execute if score #final ln matches 0 if score #pct ln matches 65.. run function ln:ch05/ev/final",
    "execute if score #tp ln matches 1.. run function ln:ch05/ev/drive",
    "execute if score #mort ln matches 1.. run function ln:ch05/ev/mortar_tick",
    "execute if score #mort ln matches ..0 if entity @e[tag=ln_mortar] run function ln:ch05/ev/mortar_tick",
    # 結束：兵力耗盡、場上清空
    "execute if score #final ln matches 1 if score #budget ln matches ..0 if score #alive ln matches 0 run function ln:ch05/to_s7",
])
# 7 收尾
fn("to_s7", [*goto(7), *bossbar("防守成功", "green"), "bossbar set ln:obj value 0",
             "kill @e[tag=ln_tech]", "kill @e[tag=ln_mortar]"])
end7 = dialogue("outro") + 5 * TPS
fn("s7", ["function ln:ch05/dlg/outro", f"execute if score #t ln matches {end7} run function ln:ch05/finish"])
fn("finish", [
    "scoreboard players set #stage ln 0",
    "bossbar set ln:obj visible false",
    "title @a times 20 100 30",
    f"title @a subtitle {jtext({'text': '感謝遊玩！把感想告訴 Claude 吧', 'color': 'gray'})}",
    f"title @a title {jtext({'text': '試做關卡完成', 'color': 'gold', 'bold': True})}",
    f"tellraw @a {jtext({'text': '[長夜] 重玩：/function ln:ch05/start　　中止：/function ln:ch05/stop', 'color': 'gold'})}",
])
fn("tick", [
    "scoreboard players add #t ln 1",
    *[f"execute if score #stage ln matches {i} run function ln:ch05/s{i}" for i in (1, 2, 3, 4, 5, 7)],
])

# ================================================================== 寫檔
if OUT.exists():
    shutil.rmtree(OUT)
for name, body in files.items():
    p = OUT / f"{name}.mcfunction"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")

o = A["origin"]
p = A["pad"]
(PACK / "build/station_place.mcfunction").write_text(
    "# 在固定位置重建 7 號氣象站（由 tools/build_level.py 產生）\n"
    f"forceload add {p[0]} {p[1]} {p[2]} {p[3]}\n"
    f"execute positioned {xyz(o)} run function ln:build/weather_station\n", encoding="utf-8")
v = A["viewpoint"]
(PACK / "view_station.mcfunction").write_text(
    "# 傳送到可以看到整座氣象站的位置（創造模式審視建築用）\n"
    "gamemode creative @s\n"
    f"tp @s {xyz(v)} facing {o[0] + 22} {o[1] + 2} {o[2] + 14}\n", encoding="utf-8")
print(f"已產生 {len(files)} 個函式到 {OUT.relative_to(ROOT)}")
