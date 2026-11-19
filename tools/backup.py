"""備份伺服器世界到 backups/（生成建築前自動執行）。

用法：python tools/backup.py [說明文字]
伺服器執行中時，會先透過 RCON 執行 save-off / save-all，備份完再 save-on。
"""
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import rcon  # noqa: E402

world = rcon.world_dir()
note = "_".join(sys.argv[1:]) or "manual"
dest = ROOT / "backups" / f"{datetime.now():%Y%m%d-%H%M%S}_{world.name}_{note}"

online = False
try:
    rcon.run(["save-off", "save-all flush"])
    online = True
except OSError:
    pass  # 伺服器沒開，直接複製

try:
    shutil.copytree(world, dest, ignore=shutil.ignore_patterns("session.lock"))
    print(f"已備份到 {dest}")
finally:
    if online:
        rcon.run(["save-on"])
