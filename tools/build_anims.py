"""產生 NPC 角色動作（Player Animator 讀的 Blockbench／GeckoLib 格式）。

輸出到 mod/src/main/resources/assets/lnai/player_animation/<名稱>.json，遊戲內用 /lnhud anim <實體> <名稱> 播放。
骨頭：head、body、torso、right_arm、left_arm、right_leg、left_leg；角度單位是度。
每個動作寫成 {骨頭: {秒數: [x, y, z]}}；loop = True 循環、False 播完回原姿勢、"hold_on_last_frame" 停在最後。
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "mod/src/main/resources/assets/lnai/player_animation"


def anim(name, length, bones, loop=False, pos=None):
    b = {}
    for bone, keys in bones.items():
        b.setdefault(bone, {})["rotation"] = {f"{t:.2f}": v for t, v in sorted(keys.items())}
    for bone, keys in (pos or {}).items():
        b.setdefault(bone, {})["position"] = {f"{t:.2f}": v for t, v in sorted(keys.items())}
    data = {"format_version": "1.8.0", "animations": {name: {
        "loop": loop, "animation_length": length, "bones": b}}}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return name


made = []


def osc(a, b, n, length):
    """在 a、b 兩個姿勢之間來回 n 次（循環動作用）"""
    return {round(i * length / (2 * n), 3): (a if i % 2 == 0 else b) for i in range(2 * n + 1)}


# 踹門（0.7 秒）：右腳往後蓄力 → 往前踹 → 收回；上身微微後仰
made.append(anim("kick", 0.7, {
    "right_leg": {0: [0, 0, 0], 0.2: [30, 0, 0], 0.32: [-85, 0, 0], 0.5: [-30, 0, 0], 0.7: [0, 0, 0]},
    "body": {0: [0, 0, 0], 0.32: [-10, 0, 0], 0.7: [0, 0, 0]},
    "left_leg": {0: [0, 0, 0], 0.32: [8, 0, 0], 0.7: [0, 0, 0]},
}))
# 攙扶（白鴉）：左手橫跨搭在別人肩上，走路時身體跟著晃
made.append(anim("support", 1.0, {
    "left_arm": osc([-15, 0, -95], [-20, 0, -100], 2, 1.0),
    "body": osc([4, 0, -3], [4, 0, 3], 1, 1.0),
    "head": {0: [10, -15, 0], 1.0: [10, -15, 0]},
}, loop=True))
# 被攙扶（情報官）：右手搭在對方肩上，彎腰低頭、左手抱胸發抖
made.append(anim("limp", 1.2, {
    "right_arm": osc([-10, 0, 100], [-15, 0, 95], 2, 1.2),
    "left_arm": osc([-55, 35, 0], [-50, 30, 0], 6, 1.2),
    "body": {0: [18, 0, 0], 0.6: [22, 0, 4], 1.2: [18, 0, 0]},
    "head": {0: [30, 10, 0], 1.2: [30, 10, 0]},
}, loop=True))
# 拍打手腕上的掃描器（狐狸）：左前臂舉在胸前、右手一直拍、低頭看
made.append(anim("wrist_tap", 0.8, {
    "left_arm": {0: [-80, 30, 0], 0.8: [-80, 30, 0]},
    "right_arm": osc([-70, -30, 0], [-55, -30, 0], 3, 0.8),
    "head": {0: [35, 15, 0], 0.8: [35, 15, 0]},
}, loop=True))
# 冷到發抖：雙手抱胸、身體快速小幅抖動
made.append(anim("shiver", 0.4, {
    "left_arm": {0: [-55, 35, 0], 0.4: [-55, 35, 0]},
    "right_arm": {0: [-55, -35, 0], 0.4: [-55, -35, 0]},
    "body": osc([3, 0, -2], [3, 0, 2], 2, 0.4),
    "head": osc([12, 0, -2], [12, 0, 2], 2, 0.4),
}, loop=True))
# 指方向：右手往前伸直指出去（停在最後的姿勢）
made.append(anim("point", 0.5, {
    "right_arm": {0: [0, 0, 0], 0.3: [-95, -8, 0], 0.5: [-92, -8, 0]},
    "head": {0: [0, 0, 0], 0.3: [-5, 0, 0], 0.5: [-5, 0, 0]},
}, loop="hold_on_last_frame"))
# 舉槍警戒（站姿微晃，用在踹門之後）
made.append(anim("guard", 2.0, {
    "body": osc([2, 0, 0], [4, 0, 0], 1, 2.0),
    "head": osc([0, -10, 0], [0, 10, 0], 1, 2.0),
}, loop=True))

for old in OUT.glob("*.json"):
    if old.stem not in made:
        old.unlink()
print(f"已產生 {len(made)} 個動作：{', '.join(made)}")
