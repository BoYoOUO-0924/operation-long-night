"""把配樂轉成遊戲用的 OGG，並寫入 sounds.json。

執行：.toolchain/tts-venv/Scripts/python.exe tools/make_music.py
來源與授權記錄在 levels/music.json（公開發佈需要）。原始 MP3 放在 music/src/（不進版本控制），
找不到時會去「下載」資料夾找同名檔案。
"""
import json
import shutil
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "levels/music.json").read_text(encoding="utf-8"))
SRC = ROOT / "music/src"
OUT = ROOT / "mod/src/main/resources/assets/lnai/sounds/music"
SOUNDS_JSON = ROOT / "mod/src/main/resources/assets/lnai/sounds.json"
TARGET_RMS = 0.12   # 每首調到差不多的響度，換曲時音量不會忽大忽小


def main():
    SRC.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    sj = json.loads(SOUNDS_JSON.read_text(encoding="utf-8")) if SOUNDS_JSON.exists() else {}
    sj = {k: v for k, v in sj.items() if not k.startswith("music.")}
    for cue, m in CFG["tracks"].items():
        src = SRC / m["file"]
        if not src.exists():
            dl = Path.home() / "Downloads" / m["file"]
            if not dl.exists():
                print(f"找不到 {m['file']}，請從 {m['page']} 下載")
                continue
            shutil.copy2(dl, src)
        wav, sr = sf.read(str(src), always_2d=True)
        rms = float(np.sqrt(np.mean(wav ** 2)))
        wav = wav * (TARGET_RMS / max(rms, 1e-6))
        peak = float(np.abs(wav).max())
        if peak > 0.98:
            wav = wav * (0.98 / peak)
        out = OUT / f"{cue}.ogg"
        # libsndfile 一次寫入很長的 OGG 會當掉（堆疊溢位），分段寫
        with sf.SoundFile(str(out), "w", sr, wav.shape[1], format="OGG", subtype="VORBIS") as f:
            data = wav.astype(np.float32)
            for i in range(0, len(data), sr * 2):
                f.write(data[i:i + sr * 2])
        sj[f"music.{cue}"] = {"category": "music", "sounds": [{"name": f"lnai:music/{cue}", "stream": True}]}
        print(f"{cue}：{m['title']}　{len(wav) / sr:.0f} 秒　{out.stat().st_size / 1e6:.1f} MB")
    SOUNDS_JSON.write_text(json.dumps(sj, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
