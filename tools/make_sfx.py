"""產生音效：程式合成的（沒有授權問題）＋ Freesound CC0 錄音（levels/sfx.json 登記來源）。

執行：.toolchain/tts-venv/Scripts/python.exe tools/make_sfx.py
輸出：mod 資源 assets/lnai/sounds/sfx/<名稱>.ogg，sounds.json 的 sfx.<名稱>
遊戲中播放：playsound lnai:sfx.<名稱> ...
"""
import json
import shutil
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "levels/sfx.json").read_text(encoding="utf-8"))
SRC = ROOT / "sfx/src"
OUT = ROOT / "mod/src/main/resources/assets/lnai/sounds/sfx"
SOUNDS_JSON = ROOT / "mod/src/main/resources/assets/lnai/sounds.json"
SR = 44100
rng = np.random.default_rng(20261120)


def t_(sec):
    return np.arange(int(sec * SR)) / SR


def env(n, a, r):
    """攻擊 a 秒、釋放 r 秒的包絡"""
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr) ** 2
    return e


def bp(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), hi / (SR / 2)], btype="band")
    return signal.lfilter(b, a, x)


def lp(x, hi, order=2):
    b, a = signal.butter(order, hi / (SR / 2))
    return signal.lfilter(b, a, x)


def smooth_noise(sec, rate):
    """慢速隨機起伏（0～1），rate = 每秒幾個變化點"""
    n = int(sec * rate) + 4
    pts = rng.random(n)
    x = np.interp(np.linspace(0, n - 3, int(sec * SR)), np.arange(n), pts)
    return lp(x, rate * 2, 1)


def echo(x, delay=0.11, fb=0.35, n=5):
    y = np.copy(x)
    d = int(delay * SR)
    for k in range(1, n + 1):
        y = y + np.pad(x, (d * k, 0))[:len(x)] * (fb ** k)
    return y


# ---------------------------------------------------------------- 合成音效
def blizzard():
    """暴風雪環境音（20 秒無縫循環，立體聲）：低沉的風聲＋陣風＋高頻的呼嘯"""
    sec = 22
    ch = []
    for c in range(2):
        noise = rng.normal(0, 1, int(sec * SR))
        brown = np.cumsum(noise)
        brown = signal.lfilter([1, -1], [1, -0.995], brown)
        brown /= np.abs(brown).max()
        gust = 0.35 + 0.65 * smooth_noise(sec, 0.35) ** 1.5
        low = lp(brown, 500) * gust
        # 呼嘯：窄頻帶通，中心頻率跟著陣風飄移
        whistle = np.zeros(int(sec * SR))
        hiss = rng.normal(0, 1, int(sec * SR))
        seg = SR // 10
        fc = 500 + 700 * smooth_noise(sec, 0.25)
        for i in range(0, len(hiss), seg):
            f = float(fc[i])
            b, a = signal.iirpeak(f / (SR / 2), 18)
            whistle[i:i + seg] = signal.lfilter(b, a, hiss[i:i + seg + 0])[:len(whistle[i:i + seg])]
        whistle *= (gust ** 2) * 0.35
        snow = bp(rng.normal(0, 1, int(sec * SR)), 2500, 7000) * 0.05 * gust
        ch.append(low * 0.9 + whistle + snow)
    x = np.stack(ch, axis=1)
    # 無縫循環：最後 2 秒和開頭交叉淡化
    loop, fade = 20, 2
    n, nf = int(loop * SR), int(fade * SR)
    out = x[:n].copy()
    w = np.linspace(0, 1, nf)[:, None]
    out[:nf] = x[n:n + nf] * (1 - w) + x[:nf] * w
    return out


def boom():
    """重低音（揭示氣象站）：低頻掃頻＋悶擊＋長尾"""
    t = t_(4.5)
    f = 62 * np.exp(-t * 0.5) + 28
    ph = 2 * np.pi * np.cumsum(f) / SR
    sub = np.sin(ph) * np.exp(-t * 0.9)
    thump = lp(rng.normal(0, 1, len(t)), 180) * np.exp(-t * 9) * 3
    rumble = lp(rng.normal(0, 1, len(t)), 90) * np.exp(-t * 0.7) * 1.2
    x = np.tanh((sub * 1.2 + thump + rumble) * 1.4)
    return x * env(len(t), 0.005, 1.2)


def beep(freq, sec, square=False):
    t = t_(sec)
    s = np.sign(np.sin(2 * np.pi * freq * t)) * 0.5 if square else np.sin(2 * np.pi * freq * t)
    return s * env(len(t), 0.004, min(0.04, sec / 2))


def scanner_fail():
    """掃描器故障：兩聲往下掉的「嗶—」＋雜訊「滋」"""
    a = beep(1400, 0.09, True)
    b = beep(900, 0.16, True)
    buzz = bp(rng.normal(0, 1, int(0.25 * SR)), 800, 3000) * env(int(0.25 * SR), 0.01, 0.15) * 0.6
    gap = np.zeros(int(0.05 * SR))
    x = np.concatenate([a, gap, b, gap, buzz])
    return bp(x, 400, 5000) * 0.8


def scanner_pulse():
    """掃描脈衝：聲納般的「咚——」加上往上掃的短音"""
    t = t_(1.6)
    ping = np.sin(2 * np.pi * 1180 * t) * np.exp(-t * 3.2)
    sweep_t = t_(0.18)
    sweep = np.sin(2 * np.pi * np.cumsum(300 + 2400 * sweep_t / 0.18) / SR) * env(len(sweep_t), 0.01, 0.08) * 0.4
    x = echo(ping, 0.13, 0.4, 4)
    x[:len(sweep)] += sweep
    return x * 0.7


def scanner_ready():
    """修好掃描器：三個往上的音"""
    parts = [beep(f, 0.12) for f in (880, 1175, 1568)]
    gap = np.zeros(int(0.04 * SR))
    x = np.concatenate([parts[0], gap, parts[1], gap, parts[2] * 1.2, np.zeros(int(0.4 * SR))])
    return echo(x, 0.09, 0.3, 3) * 0.6


def objective():
    """目標更新：低調的兩聲戰術提示音"""
    a = beep(660, 0.1) * 0.7
    b = beep(990, 0.18)
    x = np.concatenate([a, np.zeros(int(0.03 * SR)), b, np.zeros(int(0.3 * SR))])
    return echo(x, 0.07, 0.25, 3) * 0.55


def mortar_whistle():
    """迫擊砲落下的呼嘯：音高往下掉、越來越大聲"""
    sec = 2.2
    t = t_(sec)
    f = 1900 - 1300 * (t / sec) ** 1.3
    s = np.sin(2 * np.pi * np.cumsum(f) / SR)
    air = bp(rng.normal(0, 1, len(t)), 700, 2500) * 0.25
    amp = (t / sec) ** 1.8
    return (s * 0.6 + air) * amp * env(len(t), 0.2, 0.05)


def radio_on():
    """對講機按下：喀＋短暫的嘶聲"""
    click = rng.normal(0, 1, int(0.008 * SR)) * 0.9
    squelch = bp(rng.normal(0, 1, int(0.12 * SR)), 1200, 4500) * np.linspace(0.6, 0.05, int(0.12 * SR))
    return np.concatenate([click, squelch])


def radio_off():
    """對講機放開：「嘶—喀」的尾音"""
    squelch = bp(rng.normal(0, 1, int(0.22 * SR)), 900, 5000) * np.linspace(0.15, 0.7, int(0.22 * SR))
    click = rng.normal(0, 1, int(0.01 * SR)) * 0.8
    return np.concatenate([squelch, click, np.zeros(int(0.03 * SR))])


SYNTH = {
    "blizzard_loop": blizzard, "boom": boom, "scanner_fail": scanner_fail, "scanner_pulse": scanner_pulse,
    "scanner_ready": scanner_ready, "objective": objective, "mortar_whistle": mortar_whistle,
    "radio_on": radio_on, "radio_off": radio_off,
}


def write(name, x, sr=SR):
    x = np.asarray(x, dtype=np.float32)
    x = x / max(1e-6, np.abs(x).max()) * 0.9
    OUT.mkdir(parents=True, exist_ok=True)
    chans = 1 if x.ndim == 1 else x.shape[1]
    with sf.SoundFile(str(OUT / f"{name}.ogg"), "w", sr, chans, format="OGG", subtype="VORBIS") as f:
        for i in range(0, len(x), sr * 2):
            f.write(x[i:i + sr * 2])


def main():
    sj = json.loads(SOUNDS_JSON.read_text(encoding="utf-8")) if SOUNDS_JSON.exists() else {}
    sj = {k: v for k, v in sj.items() if not k.startswith("sfx.")}
    made = []
    for name, fn in SYNTH.items():
        write(name, fn())
        made.append(name)
    SRC.mkdir(parents=True, exist_ok=True)
    for name, m in CFG["recorded"].items():
        sid = m["page"].rstrip("/").split("/")[-1]   # Freesound 的檔名都是「編號__作者__名稱」
        found = sorted(SRC.glob(f"{sid}__*")) or sorted((Path.home() / "Downloads").glob(f"{sid}__*"))
        if not found:
            print(f"找不到編號 {sid} 的檔案（{m['what']}）：請從 {m['page']} 下載")
            continue
        src = SRC / found[0].name
        if not src.exists():
            shutil.copy2(found[0], src)
        x, sr = sf.read(str(src), always_2d=True)
        x = x.mean(axis=1)   # 錄音音效轉單聲道，遊戲裡才有方向感
        a, b = m.get("trim", [0, None])
        x = x[int(a * sr): int(b * sr) if b else None]
        n = int(0.02 * sr)
        if len(x) > 2 * n:
            x[:n] *= np.linspace(0, 1, n)
            x[-n:] *= np.linspace(1, 0, n)
        nf = int(m.get("fade", 0) * sr)
        if 0 < nf < len(x):
            x[-nf:] *= np.linspace(1, 0, nf) ** 2
        write(name, x, sr)
        made.append(name)
    for name in made:
        sj[f"sfx.{name}"] = {"category": "ambient" if name.endswith("_loop") else "master",
                             "sounds": [{"name": f"lnai:sfx/{name}", "stream": name.endswith("_loop")}]}
    SOUNDS_JSON.write_text(json.dumps(sj, ensure_ascii=False, indent=1), encoding="utf-8")
    print("音效：" + "、".join(made))


if __name__ == "__main__":
    main()
