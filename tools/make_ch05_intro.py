"""第五章開場過場（約 40 秒）→ levels/cutscenes/ch05_intro.json

分鏡（使用者提供，依地圖與劇情調整）：
  Shot 1 災難餘波（0～10 秒）  低角度貼地推鏡：沿著炸斷的鐵軌推進，穿過濃煙，拉高帶出翻覆的列車
  Shot 2 絕境集結（10～22 秒） 側面手持跟拍：戰車踹開卡死的鐵門架槍警戒；白鴉攙扶發抖的情報官；
                               狐狸拍打手腕上的掃描器（還是壞的，沒有訊號）
  Shot 3 目標揭示（22～34 秒） 過肩鏡頭＋大仰角搖鏡：越過風雪，定格在山上的氣象站（雷達罩、閃爍的琥珀燈）
  Shot 4 無縫接管（34～40 秒） 快速衝鏡進玩家的眼睛，冰霜外框，交還操作

執行：python tools/make_ch05_intro.py，再執行 python tools/build_level.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
W = json.loads((ROOT / "generators/out/train_wreck.json").read_text(encoding="utf-8"))
A = json.loads((ROOT / "generators/out/weather_station.json").read_text(encoding="utf-8"))
S = 20  # 每秒 tick 數

DOOR = W["door"]                  # 運兵車廂西側鐵門（下半）
DX, DY, DZ = DOOR
AMBER = A["amber_light"]
RADAR = A["radar"]
STATION_LOOK = [(AMBER[0] + RADAR[0]) / 2, (AMBER[1] + RADAR[1]) / 2, (AMBER[2] + RADAR[2]) / 2]
# Shot 3 的位置：鐵路西邊的小高地。從這裡略高的地方越過山脊，看得到雷達罩和屋頂的琥珀燈
RIDGE = [172.0, 974.0]            # 白鴉、戰車站的地方
PLAYER_SPOT = [176.5, 971.5]      # 交還操作時玩家站的位置（在他們後方）
HIDE = [205, 916]                 # 過場期間玩家先站在鏡頭拍不到的地方（Shot 1 鏡頭正後方）

cam, subs, cmds, moves, shakes = [], [], [], [], []


def key(t, pos, look=None, **kw):
    k = {"t": int(t * S), "pos": pos}
    if look:
        k["look_at"] = look
    k.update(kw)
    cam.append(k)


def at(t, *run):
    for r in run:
        cmds.append({"at": int(t * S), "run": r})


def say(t, who, text, dur=4.5):
    subs.append({"at": int(t * S), "dur": int(dur * S), "who": who, "text": text})


def move(t, dur, tag, path):
    moves.append({"at": int(t * S), "dur": int(dur * S), "tag": tag, "path": path})


def sound(t, snd, pos, vol=1.0, pitch=1.0):
    at(t, f"playsound {snd} ambient @a {pos[0]} {pos[1]} {pos[2]} {vol} {pitch}")


def anim(t, tag, name):
    at(t, f"lnhud anim @e[tag={tag}] {name}")


# ---------------------------------------------------------------- 開場準備（t=0）
at(0,
   "time set 18000",
   "weather thunder 1000000",
   f"setblock {DX} {DY} {DZ} iron_door[facing=west,half=lower,hinge=left,open=false]",
   f"setblock {DX} {DY + 1} {DZ} iron_door[facing=west,half=upper,hinge=left,open=false]",
   f"spreadplayers {HIDE[0]} {HIDE[1]} 0 1 false @a",
   # 小隊先待在翻覆的車廂裡（門內）
   f"tp @e[tag=ln_tank] {DX + 1.5} {DY} {DZ + 0.5} 90 0",
   f"tp @e[tag=ln_baiya] {DX + 2.5} {DY} {DZ + 1.6} 90 0",
   f"tp @e[tag=ln_officer] {DX + 2.5} {DY} {DZ + 0.4} 90 0",
   f"tp @e[tag=ln_fox] {DX + 3.2} {DY} {DZ - 1.2} 90 0",
   "lnhud anim @e[tag=ln_ally] stop",
   "effect clear @e[tag=ln_ally] glowing",          # 過場時拿掉隊友的發光外框
   )
# 暴風雪：每半秒在鏡頭附近噴雪花
for i in range(0, 40 * 2):
    t = i / 2
    if t < 10:
        c = [204, 113, 940 + t * 1.5]
    elif t < 22:
        c = [193, 111, 970]
    elif t < 34:
        c = [177, 130, 974]
    else:
        c = [178, 128, 972]
    n = 0.55 if 22 <= t < 34 else 1.0      # Shot 3 雪小一點，讓氣象站看得清楚
    at(t, f"particle minecraft:snowflake {c[0]} {c[1]} {c[2]} 7 4 7 0.25 {int(260 * n)} force @a",
          f"particle minecraft:white_ash {c[0]} {c[1]} {c[2]} 8 4 8 0 {int(300 * n)} force @a")

# ---------------------------------------------------------------- Shot 1 災難餘波（0～10 秒）
key(0, [201.6, 109.4, 931.0], [203.0, 109.0, 945.0], fov=52, handheld=0.25)
key(4, [201.4, 110.2, 938.5], [203.0, 109.5, 952.0], fov=54)
key(7.5, [200.8, 113.5, 944.0], [202.0, 111.0, 960.0], fov=58)
key(10, [199.5, 117.0, 947.0], [201.0, 111.0, 965.0], fov=62)
for t in (0.5, 4, 7):                                      # 遠處殘骸冒出的濃煙與火星
    at(t, "particle minecraft:large_smoke 208 113 958 1.5 1.5 3 0.02 25 force @a",
          "particle minecraft:lava 204 108 945 2 0.3 2 0 6 force @a")
sound(0, "minecraft:item.elytra.flying", [204, 112, 940], 0.6, 0.55)
sound(0.2, "minecraft:block.fire.ambient", [204, 109, 945], 1.6, 0.8)
sound(2.5, "minecraft:block.anvil.land", [208, 112, 958], 0.7, 0.5)       # 金屬扭曲的呻吟
sound(5.5, "minecraft:entity.iron_golem.damage", [207, 112, 960], 1.0, 0.5)
sound(6, "minecraft:block.fire.ambient", [209, 113, 955], 1.6, 0.7)
sound(8.5, "minecraft:block.chain.break", [203, 112, 962], 1.0, 0.5)

# ---------------------------------------------------------------- Shot 2 絕境集結（10～22 秒）
def eye(x):
    """雪溝裡某個 x 的眼睛高度（溝底每往西一格高一格，再加上雪層與眼睛高度）"""
    import math
    return 108 + max(0, 195 - math.floor(x)) + 1.9


# 鏡頭在門口北邊、雪溝裡的人眼高度，平視鐵門；小隊走出來往西爬坡時，鏡頭在他們旁邊平行跟著走
key(10, [194.6, eye(194.6) - 0.3, 972.2], [DX, DY + 1.0, DZ + 0.5], cut=True, fov=60, handheld=0.9)
key(13, [194.3, eye(194.3) - 0.3, 972.4], [DX - 1.5, DY + 0.9, DZ + 0.6], fov=60)
key(17, [192.6, eye(192.6) - 0.3, 972.8], [DX - 4.0, DY + 2.0, DZ + 1.2], fov=62)
key(22, [190.8, eye(190.8) - 0.3, 973.0], [DX - 6.5, DY + 3.6, DZ + 1.6], fov=62)
anim(10.2, "ln_tank", "kick")
at(10.55,
   f"setblock {DX} {DY} {DZ} iron_door[facing=west,half=lower,hinge=left,open=true]",
   f"setblock {DX} {DY + 1} {DZ} iron_door[facing=west,half=upper,hinge=left,open=true]",
   f"particle minecraft:cloud {DX - 0.5} {DY + 1} {DZ + 0.5} 0.3 0.6 0.3 0.05 15 force @a")
sound(10.55, "minecraft:entity.zombie.attack_iron_door", DOOR, 1.4, 0.7)
sound(10.6, "minecraft:block.anvil.land", DOOR, 0.6, 0.6)
shakes.append({"at": int(10.55 * S), "dur": 5, "amp": 1.6})
# 戰車：衝出門口，往坡上架槍警戒
move(11.0, 2.5, "ln_tank", [[DX + 1.5, DY, DZ + 0.5], [DX - 1.5, DY - 1, DZ + 0.5], [DX - 3.0, DY + 1, DZ - 0.3]])
anim(13.6, "ln_tank", "guard")
# 白鴉攙扶情報官：並肩慢慢走出來，往坡上
anim(12.0, "ln_baiya", "support")
anim(12.0, "ln_officer", "limp")
move(12.2, 9.5, "ln_baiya", [[DX + 2.5, DY, DZ + 0.9], [DX - 0.8, DY - 1, DZ + 0.9], [DX - 6.5, DY + 4, DZ + 1.8]])
move(12.2, 9.5, "ln_officer", [[DX + 2.5, DY, DZ + 0.2], [DX - 0.8, DY - 1, DZ + 0.2], [DX - 6.5, DY + 4, DZ + 1.1]])
# 狐狸：最後出來，邊走邊拍手腕上的掃描器
move(14.5, 4.0, "ln_fox", [[DX + 3.2, DY, DZ + 0.5], [DX - 0.8, DY - 1, DZ + 0.5], [DX - 3.0, DY + 1, DZ - 1.5]])
anim(16.0, "ln_fox", "wrist_tap")
say(14.2, "戰車", "媽的，軌道全被炸爛了……大家都還喘著氣嗎？", 5)
for t in (11.5, 12.3, 13.1, 14.0, 15.0, 16.2, 17.4, 18.6, 19.8):   # 踏雪聲
    sound(t, "minecraft:block.snow.step", [DX - 2, DY, DZ], 0.9, 0.8)
for t in (12.5, 15.5, 18.5):                                       # 喘息（先用相近的音效代替）
    sound(t, "minecraft:entity.horse.breathe", [DX - 2, DY + 1, DZ], 0.5, 1.6)
sound(17.0, "minecraft:block.note_block.hat", [DX - 3, DY + 1, DZ - 1.5], 0.3, 0.6)   # 掃描器沒反應的嗶聲

# ---------------------------------------------------------------- Shot 3 目標揭示（22～34 秒）
RX, RZ = RIDGE
# 切鏡的同時把小隊放到小高地上（鏡頭切換代表時間經過，他們已經爬上來了）
move(21.9, 0.15, "ln_tank", [[RX, 126, RZ - 0.9], [RX - 0.1, 126, RZ - 0.9]])
move(21.9, 0.15, "ln_baiya", [[RX, 126, RZ + 0.9], [RX - 0.1, 126, RZ + 0.9]])
move(21.9, 0.15, "ln_officer", [[RX + 1.6, 126, RZ + 2.3], [RX + 1.5, 126, RZ + 2.3]])
move(21.9, 0.15, "ln_fox", [[RX + 0.8, 126, RZ - 2.6], [RX + 0.7, 126, RZ - 2.6]])
anim(22.0, "ln_tank", "guard")
anim(22.0, "ln_baiya", "stop")
anim(22.0, "ln_officer", "shiver")
anim(26.6, "ln_fox", "point")
OTS = [RX + 2.6, 130.0, RZ]
key(22, [RX + 3.2, 128.6, RZ + 0.1], [RX - 10, 127.5, RZ], cut=True, fov=68, handheld=0.6)
key(26, OTS, STATION_LOOK, fov=46)
key(30, [OTS[0] - 0.5, OTS[1] + 0.5, OTS[2]], STATION_LOOK, fov=40, handheld=0.35)
key(34, [OTS[0] - 0.9, OTS[1] + 0.8, OTS[2]], STATION_LOOK, fov=37)
shakes.append({"at": int(26 * S), "dur": 4, "amp": 1.0})
sound(26, "minecraft:block.respawn_anchor.deplete", OTS, 1.0, 0.5)       # 低頻重音
sound(26, "minecraft:entity.generic.explode", OTS, 0.25, 0.5)
sound(22, "minecraft:item.elytra.flying", OTS, 0.25, 0.4)              # 風聲轉沉
say(27.0, "狐狸", "體溫掉太快了！兩點鐘方向山腰有座舊氣象站，先衝進去生火！", 5.5)
# 琥珀燈閃爍（亮 → 暗 → 亮）
a1 = f"{AMBER[0]} {AMBER[1]} {AMBER[2]} {AMBER[0]} {AMBER[1]} {AMBER[2] + 1}"
for i, t in enumerate([24.0, 24.4, 25.6, 25.8, 27.3, 28.9, 29.1, 31.0, 31.5]):
    at(t, f"fill {a1} {'orange_terracotta' if i % 2 == 0 else 'ochre_froglight'}")
at(32.5, f"fill {a1} ochre_froglight")

# ---------------------------------------------------------------- Shot 4 無縫接管（34～40 秒）
at(33.0,
   f"spreadplayers {PLAYER_SPOT[0]} {PLAYER_SPOT[1]} 0 2 false @a",
   f"execute as @a at @s run tp @s ~ ~ ~ facing {STATION_LOOK[0]} {STATION_LOOK[1]} {STATION_LOOK[2]}")
key(34, [186.0, 132.0, 978.0], [PLAYER_SPOT[0], 125.5, PLAYER_SPOT[1]], cut=True, fov=58, handheld=0.2)
key(37.5, [180.0, 127.6, 973.6], [PLAYER_SPOT[0] - 4, 126.5, PLAYER_SPOT[1] - 0.8], fov=66, ease="linear")
key(40, "player", ease="linear", handheld=0)
sound(39.6, "minecraft:block.glass.break", [PLAYER_SPOT[0], 126, PLAYER_SPOT[1]], 0.35, 1.9)   # 護目鏡結霜的冰裂聲
sound(39.7, "minecraft:block.powder_snow.step", [PLAYER_SPOT[0], 126, PLAYER_SPOT[1]], 1.0, 0.8)
at(39.8, "effect give @a[gamemode=adventure] slowness 8 0 true",
         "execute as @a at @s run spawnpoint @s ~ ~ ~",
         "lnhud anim @e[tag=ln_ally] stop",
         "effect give @e[tag=ln_ally,tag=!ln_officer] glowing infinite 0 true",
         "scoreboard players set #stage ln 1",
         "scoreboard players set #t ln 0")

data = {
    "_說明": "第五章開場（由 tools/make_ch05_intro.py 產生，請改腳本）",
    "letterbox": 0.11, "fade_in": 25, "fade_out": 0, "frost_after": 70, "protect": True,
    "freeze": ["ln_ally"],
    "titles": [{"at": int(1.5 * S), "dur": int(5.5 * S), "text": "第五章　寒霜陷阱", "sub": "零下四十度"}],
    "camera": cam, "shakes": shakes, "subtitles": subs, "moves": moves, "commands": cmds,
}
out = ROOT / "levels/cutscenes/ch05_intro.json"
out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{out.relative_to(ROOT)}：{len(cam)} 個鏡頭關鍵格、{len(cmds)} 個指令、{len(moves)} 段走位")
