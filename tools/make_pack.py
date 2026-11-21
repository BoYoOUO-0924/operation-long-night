"""打包給朋友的 CurseForge 匯入包（私下分享，不上架）。

執行：python tools/make_pack.py [--ip 192.168.31.209] [--version 0.5.0]
產出：dist/代號長夜-<版本>.zip　→ 朋友在 CurseForge App「建立自訂設定檔 → 匯入」選這個 zip。

內容全部放在 overrides/（模組 jar、設定檔、TaCZ 槍包、按鍵與語言、伺服器清單），manifest 的 files 留空，
所以不需要每個模組都在 CurseForge 上（lnai、GitHub 版 ZeroContact 都不在）。
模組與設定直接取自開發用的 Prism 實例「大戰場測試」，確保跟伺服器是同一版。
"""
import argparse
import io
import json
import os
import struct
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INST = Path(os.environ["APPDATA"]) / "PrismLauncher/instances/大戰場測試/minecraft"
NAME = "代號：長夜 Operation Long Night"
FORGE = "forge-47.4.16"
MC = "1.20.1"

# options.txt 只放跟這張地圖有關的設定（其他畫面、音量設定讓朋友自己調）
OPTION_KEYS = ("lang", "resourcePacks", "key_key.tacz.", "key_key.lnai.")


def nbt_servers(name, ip):
    """servers.dat（未壓縮 NBT）：多人遊戲清單預先加好這台伺服器"""
    def s(v):
        b = v.encode("utf-8")
        return struct.pack(">H", len(b)) + b

    def tag_str(k, v):
        return b"\x08" + s(k) + s(v)

    entry = tag_str("name", name) + tag_str("ip", ip) + b"\x01" + s("acceptTextures") + b"\x01" + b"\x00"
    servers = b"\x09" + s("servers") + b"\x0a" + struct.pack(">i", 1) + entry
    return b"\x0a" + s("") + servers + b"\x00"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ip", default="192.168.31.209:25565", help="伺服器位址（寫進朋友的多人遊戲清單）")
    ap.add_argument("--version", default="0.5.0")
    a = ap.parse_args()

    out = ROOT / "dist" / f"代號長夜-{a.version}.zip"
    out.parent.mkdir(exist_ok=True)
    manifest = {
        "minecraft": {"version": MC, "modLoaders": [{"id": FORGE, "primary": True}], "recommendedRam": 6144},
        "manifestType": "minecraftModpack",
        "manifestVersion": 1,
        "name": NAME,
        "version": a.version,
        "author": "BoYoOuO",
        "files": [],
        "overrides": "overrides",
    }
    n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        z.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))

        def add_tree(src, dst, skip=()):
            nonlocal n
            for f in sorted(src.rglob("*")):
                rel = f.relative_to(src)
                if f.is_file() and not any(part in skip for part in rel.parts):
                    z.write(f, f"overrides/{dst}/{rel.as_posix()}")
                    n += 1

        add_tree(INST / "mods", "mods")
        add_tree(INST / "config", "config", skip=("backup-original",))
        add_tree(INST / "tacz", "tacz", skip=(".export-state.json",))
        opts = [l for l in (INST / "options.txt").read_text(encoding="utf-8").splitlines() if l.startswith(OPTION_KEYS)]
        z.writestr("overrides/options.txt", "\n".join(opts) + "\n")
        z.writestr("overrides/servers.dat", nbt_servers("代號：長夜（主機）", a.ip))
        z.writestr("安裝說明.txt", (ROOT / "docs/朋友安裝說明.txt").read_text(encoding="utf-8").replace("{IP}", a.ip))
    mods = sorted(p.name for p in (INST / "mods").glob("*.jar"))
    print(f"{out.relative_to(ROOT)}：{n + 4} 個檔案，{out.stat().st_size / 1e6:.0f} MB")
    print("模組：" + "、".join(mods))


if __name__ == "__main__":
    main()
