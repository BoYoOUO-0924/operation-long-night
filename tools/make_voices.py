"""產生角色語音（本機 Qwen3-TTS，免費、台詞不會送到網路）。

執行：.toolchain/tts-venv/Scripts/python.exe tools/make_voices.py [--only 角色] [--redo]

流程：
  1. 每個角色、每種語氣（normal 一般／shout 喊叫）用 VoiceDesign 依 levels/voices.json 的描述
     設計一段參考音檔 → voice/ref/<角色>_<語氣>.wav（已存在就沿用，聲音才會固定）
  2. 收集所有台詞：關卡對白、戰鬥喊話、過場字幕、voices.json 的 extra_lines
  3. 用 Base 模型照參考音檔念每一句 → 原聲版 voice.<id>.ogg 和無線電版 voice.<id>.radio.ogg
  4. 寫入 mod 資源 assets/lnai/sounds/voice/ 與 sounds.json
台詞編號 id = sha1(說話的人 + "|" + 去掉標點的台詞) 前 12 碼；客戶端用同一個算法找對應的語音。
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "levels/voices.json").read_text(encoding="utf-8"))
REF = ROOT / "voice/ref"
SND = ROOT / "mod/src/main/resources/assets/lnai/sounds/voice"
SOUNDS_JSON = ROOT / "mod/src/main/resources/assets/lnai/sounds.json"
CACHE = ROOT / "voice/lines.json"   # 已產生的台詞（id → 說話的人、台詞、語氣），避免重做
REF_TAKES = 6      # 參考音檔最多做幾次
LINE_TAKES = 4     # 每句台詞最多做幾次
GOOD = 0.85        # 語音辨識和原台詞的相似度達到這個值就算清楚（辨識本身也會把「凍」聽成「動」，所以不要求 1.0）


def clean(text):
    return "".join(c for c in text if c.isalnum())


def line_id(who, text):
    return hashlib.sha1(f"{who}|{clean(text)}".encode("utf-8")).hexdigest()[:12]


def spoken(text):
    """實際念出來的字：拿掉括號裡的舞台說明，套用 speak_replace（例如俄文改成中文音譯）"""
    t = re.sub(r"（[^）]*）|\([^)]*\)", "", text)
    for k, v in CFG.get("speak_replace", {}).items():
        t = t.replace(k, v)
    return t.strip()


def style_of(who, text):
    o = CFG.get("style_override", {}).get(text)
    if o:
        return o
    return "shout" if ("！" in text or "!" in text) else "normal"


def collect():
    chars = CFG["characters"]
    out = {}

    def add(who, text):
        if who in chars and text.strip():
            out[line_id(who, text)] = {"who": who, "text": text.strip(), "style": style_of(who, text)}

    L = json.loads((ROOT / "levels/ch05_trial.json").read_text(encoding="utf-8"))
    for lines in L["dialogue"].values():
        for d in lines:
            add(d["who"], d["text"])
    for route, lines in L["callouts"].items():
        for t in lines:
            add(L["callout_speakers"][route], t)
    for f in sorted((ROOT / "levels/cutscenes").glob("*.json")):
        for s in json.loads(f.read_text(encoding="utf-8")).get("subtitles", []):
            add(s.get("who", ""), s.get("text", ""))
    for d in CFG.get("extra_lines", []):
        add(d["who"], d["text"])
    return out


def radio(wav, sr):
    """對講機效果：300～3400 Hz 帶通、輕微失真、底噪，前後加按鍵喀聲"""
    b, a = signal.butter(4, [300 / (sr / 2), 3400 / (sr / 2)], btype="band")
    y = signal.lfilter(b, a, wav)
    y = np.tanh(y * 3.0) / np.tanh(3.0)
    rng = np.random.default_rng(7)
    y = y + rng.normal(0, 0.012, len(y))
    click = np.concatenate([rng.normal(0, 0.25, int(sr * 0.012)), np.zeros(int(sr * 0.05))])
    tail = np.concatenate([np.zeros(int(sr * 0.05)), rng.normal(0, 0.18, int(sr * 0.02))])
    hiss = rng.normal(0, 0.03, int(sr * 0.08))
    y = np.concatenate([click, hiss, y, hiss, tail])
    return (y / max(1e-6, np.abs(y).max()) * 0.85).astype(np.float32)


def normalize(wav):
    wav = np.asarray(wav, dtype=np.float32)
    # 去掉頭尾靜音
    idx = np.where(np.abs(wav) > 0.01)[0]
    if len(idx):
        wav = wav[max(0, idx[0] - 800): idx[-1] + 2400]
    return wav / max(1e-6, np.abs(wav).max()) * 0.9


def write_ogg(path, wav, sr):
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), wav, sr, format="OGG", subtype="VORBIS")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="只處理這個角色")
    ap.add_argument("--redo", action="store_true", help="重做台詞（參考音檔不重做）")
    ap.add_argument("--refs-only", action="store_true", help="只做參考音檔（試聽聲音用）")
    args = ap.parse_args()

    import torch
    from qwen_tts import Qwen3TTSModel

    from check_voice import check
    from zhconv_win import to_simplified   # 繁體會被念成粵語腔：一律轉簡體再給 AI 念

    chars = CFG["characters"]
    accent = CFG.get("accent_en", "")
    REF.mkdir(parents=True, exist_ok=True)
    report = []

    # 1. 參考音檔：同樣的設定每次念出來差很多，做 REF_TAKES 次，用語音辨識挑咬字最清楚的
    need = [(w, s) for w, c in chars.items() for s in c["styles"]
            if (not args.only or w == args.only) and not (REF / f"{w}_{s}.wav").exists()]
    if need:
        vd = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign", device_map="cuda:0", dtype=torch.bfloat16)
        for w, s in need:
            c = chars[w]
            instruct = f"{c['voice_en']} {accent} Tone of this line: {c['styles_en'][s]}"
            best = None
            for k in range(REF_TAKES):
                wavs, sr = vd.generate_voice_design(text=to_simplified(c["ref_text"]), language="Chinese", instruct=instruct)
                lang, p, txt, sim = check(wavs[0], sr, c["ref_text"])
                score = sim if lang == "zh" else 0
                if best is None or score > best[0]:
                    best = (score, wavs[0], sr, txt)
                if score >= 0.95:
                    break
            sf.write(str(REF / f"{w}_{s}.wav"), normalize(best[1]), best[2])
            print(f"參考音檔：{w}_{s}　清晰度 {best[0]:.2f}　辨識：{best[3]}")
            report.append(f"參考 {w}_{s}\t{best[0]:.2f}\t{best[3]}")
        del vd
        torch.cuda.empty_cache()
    if args.refs_only:
        return

    # 2. 台詞
    lines = collect()
    done = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    todo = {i: d for i, d in lines.items()
            if (not args.only or d["who"] == args.only)
            and (args.redo or i not in done or not (SND / f"{i}.ogg").exists())}
    print(f"台詞共 {len(lines)} 句，這次要產生 {len(todo)} 句")

    if todo:
        base = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base", device_map="cuda:0", dtype=torch.bfloat16)
        prompts = {}
        for i, d in todo.items():
            key = (d["who"], d["style"] if d["style"] in chars[d["who"]]["styles"] else "normal")
            if key not in prompts:
                prompts[key] = base.create_voice_clone_prompt(
                    ref_audio=str(REF / f"{key[0]}_{key[1]}.wav"), ref_text=to_simplified(chars[key[0]]["ref_text"]), x_vector_only_mode=False)
            best = None
            for k in range(LINE_TAKES):
                wavs, sr = base.generate_voice_clone(text=to_simplified(spoken(d["text"])), language="Chinese", voice_clone_prompt=prompts[key])
                lang, p, txt, sim = check(wavs[0], sr, spoken(d["text"]))
                score = sim if lang == "zh" else 0
                if best is None or score > best[0]:
                    best = (score, wavs[0], sr, txt)
                if score >= GOOD:
                    break
            wav, sr = normalize(best[1]), best[2]
            write_ogg(SND / f"{i}.ogg", wav, sr)
            write_ogg(SND / f"{i}.radio.ogg", radio(wav, sr), sr)
            done[i] = dict(d, clarity=round(best[0], 2), heard=best[3])
            flag = "" if best[0] >= GOOD else "　⚠ 不夠清楚，請試聽"
            print(f"  {d['who']}（{d['style']}）{best[0]:.2f} {d['text']}{flag}")
            report.append(f"{d['who']}\t{best[0]:.2f}\t{d['text']}\t辨識：{best[3]}{flag}")
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(done, ensure_ascii=False, indent=1), encoding="utf-8")

    # 3. sounds.json（保留其他聲音設定，重寫 voice.* 這一段）
    sj = json.loads(SOUNDS_JSON.read_text(encoding="utf-8")) if SOUNDS_JSON.exists() else {}
    sj = {k: v for k, v in sj.items() if not k.startswith("voice.")}
    for i in sorted(done):
        if (SND / f"{i}.ogg").exists():
            sj[f"voice.{i}"] = {"category": "voice", "sounds": [{"name": f"lnai:voice/{i}", "stream": False}]}
            sj[f"voice.{i}.radio"] = {"category": "voice", "sounds": [{"name": f"lnai:voice/{i}.radio", "stream": False}]}
    SOUNDS_JSON.write_text(json.dumps(sj, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"sounds.json：{sum(1 for k in sj if k.startswith('voice.')) // 2} 句語音")
    if report:
        (ROOT / "voice/report.txt").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
