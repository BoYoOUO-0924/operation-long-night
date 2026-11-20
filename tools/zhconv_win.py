"""繁簡轉換（用 Windows 內建的 LCMapStringEx，不用另外裝套件）。

為什麼需要：Qwen3-TTS 看到繁體字容易念成粵語腔，所以台詞先轉簡體再交給 AI 念；
遊戲裡的字幕仍然是繁體。語音辨識的結果則轉回繁體再和原台詞比對。
"""
import ctypes

_LCMAP_SIMPLIFIED = 0x02000000
_LCMAP_TRADITIONAL = 0x04000000


def _map(text, flag):
    if not text:
        return text
    f = ctypes.windll.kernel32.LCMapStringEx
    n = f("zh-CN", flag, text, len(text), None, 0, None, None, 0)
    buf = ctypes.create_unicode_buffer(n)
    f("zh-CN", flag, text, len(text), buf, n, None, None, 0)
    return buf.value[:n]


def to_simplified(text):
    return _map(text, _LCMAP_SIMPLIFIED)


def to_traditional(text):
    return _map(text, _LCMAP_TRADITIONAL)


if __name__ == "__main__":
    s = to_simplified("少廢話，動作快一點，不想死在這裡就給我跟上。")
    print(s, "→", to_traditional(s))
