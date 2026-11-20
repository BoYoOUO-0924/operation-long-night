"""用本機語音辨識（faster-whisper large-v3-turbo）檢查語音：辨識出的語言、內容，以及和原台詞的相似度。

用法：.toolchain/tts-venv/Scripts/python.exe tools/check_voice.py 檔案.wav [...]
也可以在其他腳本 import：check(wav, sr, expected_text) → (語言, 機率, 辨識文字, 相似度)
"""
import difflib
import sys

import numpy as np
import soundfile as sf
from scipy import signal

_model = None


def model():
    global _model
    if _model is None:
        # ctranslate2 需要 CUDA 12 的 cublas／cudnn，借用 PyTorch 內附的 DLL
        import os
        import torch
        lib = os.path.join(os.path.dirname(torch.__file__), "lib")
        os.environ["PATH"] = lib + os.pathsep + os.environ.get("PATH", "")
        os.add_dll_directory(lib)
        from faster_whisper import WhisperModel
        _model = WhisperModel("large-v3-turbo", device="cuda", compute_type="float16")
    return _model


def _16k(wav, sr):
    wav = np.asarray(wav, dtype=np.float32)
    if wav.ndim > 1:
        wav = wav.mean(axis=1)
    if sr != 16000:
        wav = signal.resample_poly(wav, 16000, sr).astype(np.float32)
    return wav


def _clean(t):
    from zhconv_win import to_simplified   # 兩邊都轉簡體再比（辨識結果有時是簡體、有時是繁體）
    return "".join(c for c in to_simplified(t) if c.isalnum())


def check(wav, sr, expected=None):
    a = _16k(wav, sr)
    segs, info = model().transcribe(a, beam_size=1, language=None)
    txt = "".join(s.text for s in segs).strip()
    sim = None
    if expected:
        sim = difflib.SequenceMatcher(None, _clean(txt), _clean(expected)).ratio()
    return info.language, info.language_probability, txt, sim


if __name__ == "__main__":
    for f in sys.argv[1:]:
        w, sr = sf.read(f)
        lang, p, txt, _ = check(w, sr)
        print(f"{f}\t{lang} {p:.2f}\t{txt}")
