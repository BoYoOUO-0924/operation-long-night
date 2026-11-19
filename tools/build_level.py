"""把關卡設定（levels/*.json + 建築錨點）編譯成資料包函式。

執行：python tools/build_level.py
產生：datapack/longnight/data/ln/functions/ch05/**（請勿手動修改這些檔案）

階段（#stage ln）：
  1 approach 上山   2 arrival 抵達   3 reveal 揭露   4 prepare 準備防守
  5 combat 波次戰鬥  6 between 波次間  7 outro 收尾   0 未進行
"""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACK = ROOT / "datapack/longnight/data/ln/functions"
OUT = PACK / "ch05"
A = json.loads((ROOT / "generators/out/weather_station.json").read_text(encoding="utf-8"))
L = json.loads((ROOT / "levels/ch05_trial.json").read_text(encoding="utf-8"))
SPK = L["speakers"]
TPS = 20

files = {}


def fn(name, lines):
    files[name] = "# 由 tools/build_level.py 自動產生，請勿手動修改\n" + "\n".join(lines) + "\n"


def xyz(p):
    return f"{p[0]} {p[1]} {p[2]}"


def jtext(obj):
    return json.dumps(obj, ensure_ascii=False)


def say_line(who, text):
    color = SPK.get(who, "white")
    if who == "目標":
        return [f"tellraw @a {jtext([{'text': '▶ 目標：', 'color': color, 'bold': True}, {'text': text, 'color': 'white'}])}",
                f"title @a actionbar {jtext({'text': text, 'color': color})}",
                "execute as @a at @s run playsound minecraft:block.note_block.bell master @s ~ ~ ~ 0.6 1.2"]
    if who == "提示":
        return [f"tellraw @a {jtext([{'text': '（提示）', 'color': color}, {'text': text, 'color': 'gray', 'italic': True}])}"]
    sound = ("minecraft:block.note_block.basedrum master @s ~ ~ ~ 0.8 0.5" if who == "守夜人"
             else "minecraft:ui.button.click master @s ~ ~ ~ 0.3 1.8")
    return [f"tellraw @a {jtext([{'text': f'[{who}] ', 'color': color, 'bold': True}, {'text': text, 'color': 'white'}])}",
            f"execute as @a at @s run playsound {sound}"]


def dialogue(key):
    lines = []
    for d in L["dialogue"][key]:
        t = int(d["at"] * TPS)
        for cmd in say_line(d["who"], d["text"]):
            lines.append(f"execute if score #t ln matches {t} run {cmd}")
    fn(f"dlg/{key}", lines)
    return int(max(d["at"] for d in L["dialogue"][key]) * TPS)


def bossbar(name, color="yellow"):
    return [f"bossbar set ln:obj name {jtext({'text': name})}", f"bossbar set ln:obj color {color}"]


def goto(stage):
    return [f"scoreboard players set #stage ln {stage}", "scoreboard players set #t ln 0"]


# ------------------------------------------------------------------ 隊友
ALLIES = [  # tag, 名字, 顏色, 模板
    ("ln_baiya", "白鴉", "aqua", "blue_sniper"),
    ("ln_tank", "戰車", "gold", "blue_support"),
    ("ln_fox", "狐狸", "green", "blue_assault"),
    ("ln_officer", "情報官", "gray", "ln_officer"),
]


def summon_ally(tag, name, color, template, pos="~ ~ ~"):
    extra = ",NoAI:1b" if tag == "ln_officer" else ""
    nbt = (f'{{template:"{template}",CustomName:\'{jtext({"text": name, "color": color})}\',CustomNameVisible:1b,'
           f'Invulnerable:1b,PersistenceRequired:1b{extra},Tags:["ln","ln_ally","{tag}","ln_new"]}}')
    return f"summon tacznpcs:npc {pos} {nbt}"


sx, sz = A["start_center"]
fn("spawn_allies_start", [summon_ally(*a, pos=f"{sx} 250 {sz}") for a in ALLIES] + [
    f"spreadplayers {sx} {sz} 2 5 false @e[tag=ln_new]",
    "tag @e[tag=ln_new] remove ln_new",
])

# ------------------------------------------------------------------ 敵人與波次
def enemy(center, template):
    x, z = A["enemy_spawns"][center]
    return f'summon tacznpcs:npc {x} 250 {z} {{template:"{template}",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_new_{center}"]}}'


def place(centers):
    out = []
    for c in centers:
        x, z = A["enemy_spawns"][c]
        out += [f"execute if entity @e[tag=ln_new_{c}] run spreadplayers {x} {z} 2 8 false @e[tag=ln_new_{c}]",
                f"tag @e[tag=ln_new_{c}] remove ln_new_{c}"]
    return out + ["tag @e[tag=ln_new] remove ln_new"]


WAVES = {
    # 基本兵力（1 人時）；extra = 每多 1 名玩家增加的兵力
    1: {"base": [("east", "red_assault"), ("east", "red_assault"), ("east", "red_cqb"), ("east", "red_support")],
        "extra": [("east", "red_assault"), ("east", "red_cqb")]},
    2: {"base": [("north", "red_assault"), ("north", "red_assault"), ("north", "red_support"),
                 ("south", "red_assault"), ("south", "red_cqb"), ("south", "red_cqb")],
        "extra": [("north", "red_assault"), ("south", "red_assault")]},
    3: {"base": [("east", "red_assault"), ("east", "red_assault"), ("east", "red_support"), ("east", "red_cqb"),
                 ("west", "red_sniper"), ("west", "red_sniper"), ("west", "red_assault"),
                 ("north", "red_assault"), ("north", "red_cqb"), ("north", "red_support")],
        "extra": [("east", "red_assault"), ("north", "red_assault"), ("west", "red_assault")]},
}
for n, w in WAVES.items():
    centers = sorted({c for c, _ in w["base"] + w["extra"]})
    lines = [enemy(c, t) for c, t in w["base"]]
    fn(f"wave/extra{n}", [enemy(c, t) for c, t in w["extra"]])
    lines += [f"execute if score #players ln matches {k}.. run function ln:ch05/wave/extra{n}" for k in (2, 3, 4)]
    lines += place(centers)
    lines += [f"execute store result bossbar ln:obj max if entity @e[tag=ln_enemy]",
              f"function ln:ch05/dlg/wave{n}"]
    fn(f"wave/spawn{n}", lines)

# ------------------------------------------------------------------ 裝備
fn("ammo", [
    'give @a[gamemode=adventure] tacz:ammo{AmmoId:"tacz:556x45"} 120',
    'give @a[gamemode=adventure] tacz:ammo{AmmoId:"tacz:9mm"} 34',
])
fn("loadout", [
    'give @a[gamemode=adventure] tacz:modern_kinetic_gun{GunId:"tacz:m4a1",GunCurrentAmmoCount:30,HasBulletInBarrel:1b} 1',
    'give @a[gamemode=adventure] tacz:modern_kinetic_gun{GunId:"tacz:glock_17",GunCurrentAmmoCount:17,HasBulletInBarrel:1b} 1',
    "function ln:ch05/ammo",
    "give @a[gamemode=adventure] cooked_beef 16",
])

# ------------------------------------------------------------------ 流程
fn("cleanup", [
    "kill @e[tag=ln]",
    "scoreboard players set #stage ln 0",
    "bossbar set ln:obj visible false",
    "effect clear @a",
])
fn("start", [
    "function ln:ch05/cleanup",
    "forceload add 50 900 240 1020",
    "function ln:build/station_place",
    "kill @e[type=item]",
    "time set 18000",
    "weather thunder 1000000",
    "scoreboard players set #wave ln 0",
    "gamemode adventure @a",
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

# 1 上山
dialogue("approach")
fn("s1", [
    "function ln:ch05/dlg/approach",
    "effect give @a[gamemode=adventure] slowness 2 0 true",
    "execute at @a run particle minecraft:snowflake ~ ~2 ~ 6 2 6 0.02 25 normal @a",
    f"execute positioned {xyz(A['garage_door_outside'])} if entity @a[gamemode=adventure,distance=..9] run function ln:ch05/to_s2",
])
fn("to_s2", [
    *goto(2),
    f"tp @e[tag=ln_fox] {xyz(A['fox_bench'])}",
    f"tp @e[tag=ln_tank] {xyz(A['tank_radio'])}",
    f"tp @e[tag=ln_officer] {xyz(A['officer_radio'])}",
    f"tp @e[tag=ln_baiya] {xyz(A['baiya_tower'])}",
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
fn("to_s4", [*goto(4), "function ln:ch05/ammo", *bossbar("準備防守：敵軍即將抵達", "red"),
             "bossbar set ln:obj max 400"])
# 4 準備
dialogue("prepare")
fn("s4", [
    "function ln:ch05/dlg/prepare",
    "execute store result bossbar ln:obj value run scoreboard players get #t ln",
    "execute if score #t ln matches 400 run function ln:ch05/next_wave",
])
# 5 戰鬥
for n in WAVES:
    dialogue(f"wave{n}")
fn("next_wave", [
    "scoreboard players add #wave ln 1",
    *goto(5),
    "execute store result score #players ln if entity @a[gamemode=adventure]",
    "execute if score #players ln matches ..0 run scoreboard players set #players ln 1",
    *[f"execute if score #wave ln matches {n} run function ln:ch05/wave/spawn{n}" for n in WAVES],
])
name_json = jtext([{"text": "第 ", "color": "red"}, {"score": {"name": "#wave", "objective": "ln"}, "color": "red"},
                   {"text": f" / {len(WAVES)} 波　剩餘敵人：", "color": "red"},
                   {"score": {"name": "#enemies", "objective": "ln"}, "color": "white"}])
fn("s5", [
    *[f"execute if score #wave ln matches {n} run function ln:ch05/dlg/wave{n}" for n in WAVES],
    "execute store result score #enemies ln if entity @e[tag=ln_enemy]",
    "execute store result bossbar ln:obj value run scoreboard players get #enemies ln",
    f"bossbar set ln:obj name {name_json}",
    "execute if score #t ln matches 1800 run effect give @e[tag=ln_enemy] glowing 600 0 true",
    f"execute if score #t ln matches 1800 run tellraw @a {jtext({'text': '（提示）剩下的敵人已標示發光。', 'color': 'dark_aqua'})}",
    "execute if score #t ln matches 4800 run kill @e[tag=ln_enemy]",
    "execute if score #t ln matches 60.. if score #enemies ln matches 0 run function ln:ch05/wave_cleared",
])
fn("wave_cleared", [
    f"execute if score #wave ln matches ..{len(WAVES) - 1} run function ln:ch05/to_s6",
    f"execute if score #wave ln matches {len(WAVES)}.. run function ln:ch05/to_s7",
])
fn("to_s6", [*goto(6), *bossbar("下一波即將到來：補充彈藥", "yellow"), "function ln:ch05/ammo"])
dialogue("between")
fn("s6", ["function ln:ch05/dlg/between", "execute if score #t ln matches 240 run function ln:ch05/next_wave"])
# 7 收尾
fn("to_s7", [*goto(7), *bossbar("防守成功", "green"), "bossbar set ln:obj value 0"])
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
    *[f"execute if score #stage ln matches {i} run function ln:ch05/s{i}" for i in range(1, 8)],
])

# ------------------------------------------------------------------ 寫檔
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
