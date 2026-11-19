"""讀取玩家在遊戲裡用 ln_tool 放的標記（類型、編號、座標、面向）。

用法：python tools/marks.py          # 列出所有標記
      python tools/marks.py --json   # 輸出 JSON（給關卡編譯用）
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rcon  # noqa: E402

LABEL = {"trigger": "觸發點", "enemy": "敵人生成點", "ally": "隊友位置",
         "checkpoint": "存檔點", "camera": "鏡頭位置", "note": "備註"}


def read_marks():
    res = rcon.run(["execute as @e[type=marker,tag=ln_mark] run data get entity @s"])[0][1]
    marks = []
    for chunk in res.split("Marker has the following entity data: ")[1:]:
        pos = re.search(r"Pos: \[([-\d.]+)d, ([-\d.]+)d, ([-\d.]+)d\]", chunk)
        rot = re.search(r"Rotation: \[([-\d.]+)f, ([-\d.]+)f\]", chunk)
        mid = re.search(r"id: (\d+)", chunk)
        typ = re.search(r'type: "(\w+)"', chunk)
        if pos and typ:
            marks.append({"id": int(mid.group(1)) if mid else 0, "type": typ.group(1),
                          "pos": [round(float(v), 1) for v in pos.groups()],
                          "rot": [round(float(v), 1) for v in rot.groups()] if rot else None})
    return sorted(marks, key=lambda m: m["id"])


if __name__ == "__main__":
    marks = read_marks()
    if "--json" in sys.argv:
        print(json.dumps(marks, ensure_ascii=False, indent=2))
    elif not marks:
        print("目前沒有任何標記。")
    else:
        for m in marks:
            x, y, z = m["pos"]
            print(f"#{m['id']:<3} {LABEL.get(m['type'], m['type']):<6} ({x}, {y}, {z})" +
                  (f"  面向 {m['rot'][0]}°" if m["rot"] else ""))
