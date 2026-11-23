"""第一章開場與結尾過場 → levels/cutscenes/ch01_intro.json、ch01_outro.json

開場（35 秒，依 docs/第一章劇本.md 的分鏡）
  Shot 1 雲層（0～8 秒）     雲裡往下看，高射砲在四周炸開，風聲。章節標題。正下方海面上看得到艦隊的燈。
  Shot 2 海岸全景（8～18 秒） 穿出雲層往西推，整片黑石海岸、探照燈；三座雷達依序亮紅框（北崖 → 中央 → 燈塔）。
  Shot 3 隊友（18～28 秒）   在三位隊友旁邊一起往下墜，鏡頭往下帶到沙灘上閃綠光的紅外線信標。
  Shot 4 交還（28～35 秒）   鏡頭衝進玩家眼睛，玩家在半空中開始傘降。
  過場期間玩家站在空投點底下的屏障方塊上（看不到），結束時 ln:ch01/jump 拿掉屏障、開傘。

結尾（24 秒，抵達懸崖觀測站後）
  Shot 1 接線（0～7 秒）     觀測站裡手持鏡頭：戰車接上有線電話，海神的聲音斷斷續續回來。
  Shot 2 拉出（7～14 秒）    鏡頭穿出東側窗戶、越過崖邊：燃燒的砲台、海上的艦隊燈光。
  Shot 3 回望（14～24 秒）   從艦隊旁邊回望海岸，山體裂縫閃一下藍光（巨砲本體不出現，留給第二章）。
                             章節標題 → 淡出 → ln:ch01/outro_end 回大廳。
  第二章從觀測站用望遠鏡找巨砲位置開始，所以結尾停在「海神要座標」。

執行：python tools/make_ch01_cuts.py，再執行 python tools/build_level.py（編進資料包）
艦隊位置跟 tools/build_ch01.py 的 SHIPS 一致。
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
A = json.loads((ROOT / "generators/out/blackstone_coast.json").read_text(encoding="utf-8"))
S = 20

SHIPS = [(165, 1300), (175, 1350), (168, 1405), (178, 1455)]   # 同 build_ch01.py
HIDE = (SHIPS[1][0] + 0.5, 60, SHIPS[1][1] + 0.5)              # 結尾 Shot 3 玩家躲在 2 號艦的船殼裡（拍不到，又能載入海岸）
DROP = [(122, 300, 1406), (126, 300, 1414), (122, 300, 1422), (128, 300, 1428)]
BEACON = A["beacon"]
CRACK = A["mountain_crack"]
OBS = A["observation_post"]                                    # 觀測站地板上一格（22, 111, 1266）
COL = {"白鴉": "#55FFFF", "戰車": "#FFAA00", "狐狸": "#55FF55", "海神": "#00AAAA", "目標": "#FFFF55"}


class Cut:
    def __init__(self):
        self.cam, self.subs, self.cmds, self.moves, self.shakes, self.titles = [], [], [], [], [], []

    def key(self, t, pos, look=None, **kw):
        k = {"t": int(t * S), "pos": pos}
        if look:
            k["look_at"] = look
        k.update(kw)
        self.cam.append(k)

    def at(self, t, *run):
        for r in run:
            self.cmds.append({"at": int(t * S), "run": r})

    def say(self, t, who, text, dur=4.5):
        self.subs.append({"at": int(t * S), "dur": int(dur * S), "who": who, "color": COL.get(who, "#F2F0EA"), "text": text})

    def move(self, t, dur, tag, path):
        self.moves.append({"at": int(t * S), "dur": int(dur * S), "tag": tag, "path": path, "ground": False})

    def shake(self, t, dur=6, amp=1.2):
        self.shakes.append({"at": int(t * S), "dur": dur, "amp": amp})

    def cam_at(self, t):
        """鏡頭在 t 秒的大概位置（線性內插，給音效和粒子定位用；cut 的格子是新一段的起點）"""
        ks = [k for k in self.cam if isinstance(k["pos"], list)]
        tt = t * S
        for a, b in zip(ks, ks[1:]):
            if b["t"] > a["t"] and not b.get("cut") and a["t"] <= tt <= b["t"]:
                f = (tt - a["t"]) / (b["t"] - a["t"])
                return [a["pos"][i] + (b["pos"][i] - a["pos"][i]) * f for i in range(3)]
        return max((k for k in ks if k["t"] <= tt), key=lambda k: k["t"], default=ks[0])["pos"]

    def sound(self, t, snd, pos=None, vol=10.0, pitch=1.0):
        """音效放在鏡頭位置；音量大於 1 = 聽得到的距離是 16×音量（玩家本人離鏡頭可能上百格）"""
        p = pos or self.cam_at(t)
        self.at(t, f"playsound {snd} master @a {p[0]:.1f} {p[1]:.1f} {p[2]:.1f} {vol} {pitch}")

    def dump(self, name, **extra):
        data = {"_說明": f"第一章過場（由 tools/make_ch01_cuts.py 產生，請改腳本）", **extra,
                "camera": self.cam, "shakes": self.shakes, "subtitles": self.subs, "moves": self.moves,
                "commands": sorted(self.cmds, key=lambda c: c["at"]), "titles": self.titles}
        out = ROOT / f"levels/cutscenes/{name}.json"
        out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{out.relative_to(ROOT)}：{len(self.cam)} 個鏡頭關鍵格、{len(self.cmds)} 個指令、{len(self.subs)} 句字幕")


def frame(tag, box, color, block):
    """發光外框（Glowing 的輪廓隔著地形也看得到 → 目鏡標記）"""
    x1, y1, z1, x2, y2, z2 = box
    return (f'summon block_display {x1} {y1} {z1} {{Tags:["ln","{tag}"],Glowing:1b,glow_color_override:{color},view_range:12f,'
            f'brightness:{{sky:15,block:15}},block_state:{{Name:"minecraft:{block}"}},'
            f"transformation:{{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],"
            f"scale:[{x2 - x1 + 1}f,{y2 - y1 + 1}f,{z2 - z1 + 1}f]}}}}")


# ====================================================================== 開場
c = Cut()
# Shot 1 雲層（0～8 秒）：Minecraft 的雲在 y192，鏡頭從雲上往下穿
c.key(0, [192, 207, 1450], [150, 64, 1405], fov=60, handheld=0.9)
c.key(4, [188, 201, 1444], [140, 70, 1405], fov=60)
c.key(8, [182, 193, 1436], [100, 100, 1395], fov=62, handheld=0.6)
# Shot 2 海岸全景（8～18 秒）
c.key(13, [168, 178, 1420], [55, 125, 1370], fov=58, handheld=0.3)
c.key(18, [152, 166, 1408], [45, 125, 1375], fov=54)
# Shot 3 跟著隊友往下墜（18～28 秒）
# 注意：y304 以上是世界最頂層的區段，實體在那裡不會被畫出來，所以整段壓在 y303 以下
FALL = {"ln_baiya": ([131, 299.5, 1413], [129, 279.5, 1412]),
        "ln_tank": ([135, 301, 1417], [133, 281, 1417]),
        "ln_fox": ([132, 298, 1421], [130, 278, 1421])}
c.key(18, [142, 305, 1426], [132.7, 299, 1417], cut=True, fov=58, handheld=0.5)
c.key(23, [140.5, 299.5, 1424.5], [132.2, 292.8, 1416.8], fov=58)
c.key(28, [138, 294, 1422], [BEACON[0], BEACON[1], BEACON[2]], fov=60)
# Shot 4 衝進玩家眼睛（28～35 秒）
c.key(31.5, [127, 298, 1410.5], [100, 262, 1406], fov=66, ease="linear")
c.key(35, "player", ease="linear", handheld=0)

c.at(0, "lnhud anim @e[tag=ln_ally] stop", "effect clear @e[tag=ln_ally] glowing")
# 雲：鏡頭前方一直噴雲霧，越接近 8 秒越稀
for i in range(0, 36):
    t = i / 4
    p = c.cam_at(t)
    n = int(60 * (1 - t / 9))
    c.at(t, f"particle minecraft:cloud {p[0] - 5:.1f} {p[1] - 4:.1f} {p[2] - 3:.1f} 7 3 7 0.01 {n} force @a")
# 高射砲在四周炸開
FLAK = [(0.8, (14, -8, -16)), (2.0, (-16, -5, -10)), (3.1, (8, -12, 12)), (4.4, (-10, -9, -20)),
        (5.6, (18, -14, 4)), (6.9, (-6, -16, -14)), (9.5, (-22, -10, -18)), (11.8, (-30, -6, 10))]
for t, (dx, dy, dz) in FLAK:
    p = c.cam_at(t)
    q = f"{p[0] + dx:.1f} {p[1] + dy:.1f} {p[2] + dz:.1f}"
    c.at(t, f"particle minecraft:explosion {q} 2 2 2 0 5 force @a", f"particle minecraft:flash {q} 0 0 0 0 1 force @a",
         f"particle minecraft:large_smoke {q} 2.5 2.5 2.5 0.03 40 force @a")
    c.sound(t, "lnai:sfx.boom", vol=10, pitch=1.15)
    c.sound(t + 0.05, "minecraft:entity.generic.explode", vol=10, pitch=0.9)
    c.shake(t, 6, 1.3 if t < 8 else 0.7)
c.sound(0, "minecraft:item.elytra.flying", vol=10, pitch=0.55)
c.sound(9, "minecraft:item.elytra.flying", vol=10, pitch=0.6)
c.sound(18, "minecraft:item.elytra.flying", vol=10, pitch=0.7)
c.sound(26, "minecraft:item.elytra.flying", vol=10, pitch=0.75)
c.sound(1.6, "lnai:sfx.radio_on", vol=10)
c.titles.append({"at": int(1.5 * S), "dur": int(5.5 * S), "text": "第一章　雷霆空降", "sub": "黑石海岸"})
c.say(2, "海神", "獵犬小隊，這裡是海神。你們已經進入黑石海岸上空。", 4.6)
c.say(7, "海神", "艦隊正在接近。那三座雷達不倒，我們就是瞎子。", 4.4)
c.say(11.6, "狐狸", "三座雷達都標進你們的目鏡了：北崖、砲台中央、燈塔頂上。", 5.2)
# 三座雷達依序亮紅框（亮 → 閃一下 → 留著），17.5 秒收掉
RED = 16726832
for i, (r, t) in enumerate((("a", 12.0), ("b", 13.5), ("c", 15.0))):
    box = A[f"radar_{r}_box"]
    tag = f"c1_frame{r}"
    c.at(t, frame(tag, box, RED, "red_stained_glass"))
    c.at(t + 0.35, f"kill @e[tag={tag}]")
    c.at(t + 0.6, frame(tag, box, RED, "red_stained_glass"))
    c.sound(t, "lnai:sfx.scanner_pulse", vol=10, pitch=1.2 + 0.1 * i)
c.at(18, "kill @e[tag=c1_framea]", "kill @e[tag=c1_frameb]", "kill @e[tag=c1_framec]")
# 隊友一起往下墜（凍結 AI，用走位拉著）
for tag, (p0, p1) in FALL.items():
    c.move(18, 17, tag, [p0, p1])
# 沙灘信標閃綠光
GREEN = 4259680
bb = [BEACON[0], BEACON[1], BEACON[2], BEACON[0], BEACON[1] + 1, BEACON[2]]
for k in range(0, 20):
    t = 20 + k * 0.7
    c.at(t, frame("c1_bcn", bb, GREEN, "lime_stained_glass") if k % 2 == 0 else "kill @e[tag=c1_bcn]")
c.at(34.5, "kill @e[tag=c1_bcn]")
c.say(19.5, "狐狸", "看到沙灘上的綠點了嗎？那是紅外線信標，只有我們的目鏡看得到。", 5)
c.say(25, "白鴉", "探照燈在掃。別讓光照到你，會引來高射砲。", 4.4)
c.sound(29.5, "minecraft:item.elytra.flying", vol=10, pitch=0.9)
c.at(34.9, "function ln:ch01/jump")
c.dump("ch01_intro", letterbox=0.11, fade_in=25, fade_out=0, protect=True, freeze=["ln_ally"])

# ====================================================================== 結尾
o = Cut()
OX, OY, OZ = OBS
# Shot 1 觀測站裡（0～7 秒）：鏡頭在西南角，看東北角的有線電話（織布機當電話座）
o.key(0, [OX - 1.3, OY + 1.9, OZ + 1.6], [OX + 2, OY + 1.0, OZ - 1.6], fov=62, handheld=0.6)
o.key(7, [OX - 0.9, OY + 1.8, OZ + 1.1], [OX + 2, OY + 1.0, OZ - 1.6], fov=58)
# Shot 2 穿出東側窗戶、越過崖邊（7～14 秒）
LOOK2 = [115, 80, 1400]
o.key(7, [OX + 2.2, OY + 1.6, OZ], LOOK2, cut=True, fov=66, handheld=0.4)
o.key(10.5, [44, 121, 1261], LOOK2, fov=66)
o.key(14, [54, 124, 1256], LOOK2, fov=62)
# Shot 3 從艦隊旁邊回望海岸（14～24 秒）
LOOK3 = [10, 136, 1415]
o.key(14, [190, 76, 1336], LOOK3, cut=True, fov=50, handheld=0.25)
o.key(24, [184, 79, 1339], [10, 139, 1415], fov=44)

P = "@a[gamemode=adventure]"
o.at(0,
     f"tp {P} {OX} {OY} {OZ + 5.5} 180 0",                          # 玩家站到門外（鏡頭背後）
     f"tp @e[tag=ln_tank] {OX + 1.4} {OY} {OZ - 1.4} -135 10",
     f"tp @e[tag=ln_fox] {OX - 0.8} {OY} {OZ - 1.2} -110 20",
     f"tp @e[tag=ln_baiya] {OX + 2.3} {OY} {OZ + 1.3} -90 0",
     "lnhud anim @e[tag=ln_ally] stop",
     "effect clear @e[tag=ln_ally] glowing",
     "lnhud anim @e[tag=ln_fox] wrist_tap",
     "lnhud anim @e[tag=ln_baiya] guard",
     "lnhud music @a ch05_after 60")
o.sound(0.4, "lnai:sfx.radio_on", [OX + 2, OY + 1, OZ - 2], vol=1.5, pitch=0.8)
o.sound(4.2, "lnai:sfx.radio_on", [OX + 2, OY + 1, OZ - 2], vol=1.5, pitch=0.6)
o.say(0.6, "戰車", "線路是通的！海神、海神，這裡是獵犬，聽得到嗎？", 4)
o.say(4.6, "海神", "（雜訊）……獵犬……有線線路……收到。說吧。", 4)
o.say(8.8, "白鴉", "山裡藏著東西，剛才的干擾就是它。艦隊還在它的射程裡。", 5)
o.say(14.2, "海神", "我需要座標。給我一個目標，獵犬。", 4.2)
o.say(18.6, "狐狸", "天亮之前……我們會找到它。", 3.6)
# 燃燒的砲台：飛彈落點冒濃煙和火
FIRES = [(22, 1300), (30, 1330), (12, 1340), (40, 1290), (18, 1318), (36, 1350), (50, 1372), (60, 1400), (66, 1430), (98, 1450)]
HM = json.loads((ROOT / "generators/out/heightmap_ch01.json").read_text(encoding="utf-8"))
top = HM["solid"] if "solid" in HM else HM["top"]
for i in range(0, 24):
    for (x, z) in FIRES[i % 2::2]:
        y = top[z - HM["z1"]][x - HM["x1"]] + 1
        o.at(i + 0.5 * (i % 2), f"particle minecraft:campfire_signal_smoke {x} {y} {z} 1 0.5 1 0.02 4 force @a",
             f"particle minecraft:flame {x} {y} {z} 1.2 0.4 1.2 0.02 12 force @a",
             f"particle minecraft:lava {x} {y} {z} 1 0.3 1 0 2 force @a")
# 玩家換到 2 號艦船殼裡（Shot 3 的鏡頭在艦隊旁邊，玩家要在附近才載得到那一帶）
o.at(13.5, f"tp {P} {HIDE[0]} {HIDE[1]} {HIDE[2]}")
o.sound(14.1, "minecraft:weather.rain", vol=6, pitch=0.8)
# 山體裂縫閃一下藍光
o.at(15.6,
     f"summon block_display {CRACK[0]} {CRACK[1]} {CRACK[2]} "
     '{Tags:["ln","c1_glow"],brightness:{sky:15,block:15},block_state:{Name:"minecraft:light_blue_stained_glass"},Glowing:1b,glow_color_override:6737151,'
     "view_range:12f,transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[-1f,-6f,-3f],scale:[2f,12f,6f]}}",
     f"particle minecraft:electric_spark {CRACK[0]} {CRACK[1]} {CRACK[2]} 2 6 3 0.4 200 force @a")
o.at(16.9, "kill @e[tag=c1_glow]")
o.sound(15.4, "minecraft:entity.warden.heartbeat", vol=10, pitch=0.5)
o.sound(15.6, "minecraft:block.beacon.ambient", vol=10, pitch=0.5)
o.sound(16.6, "minecraft:entity.warden.heartbeat", vol=10, pitch=0.5)
o.shake(15.6, 24, 0.6)
o.titles.append({"at": int(19 * S), "dur": int(4.6 * S), "text": "第一章　雷霆空降", "sub": "任務完成"})
o.at(23.6, "function ln:ch01/outro_end")
o.dump("ch01_outro", letterbox=0.11, fade_in=15, fade_out=40, protect=True, freeze=["ln_ally"])
