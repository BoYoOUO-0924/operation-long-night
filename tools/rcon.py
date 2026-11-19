"""對本機 Minecraft 伺服器送出指令（RCON）。

用法：
    python tools/rcon.py "list" "time set night"
    python tools/rcon.py --deploy        # 把 datapack/ 同步到伺服器世界並 /reload
"""
import shutil
import socket
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOST, PORT = "127.0.0.1", 25575
PASSWORD = (ROOT / ".secrets" / "rcon_password.txt").read_text(encoding="utf-8").strip()


def _packet(req_id: int, ptype: int, body: str) -> bytes:
    data = struct.pack("<ii", req_id, ptype) + body.encode("utf-8") + b"\x00\x00"
    return struct.pack("<i", len(data)) + data


def _recv(sock: socket.socket):
    raw = b""
    while len(raw) < 4:
        raw += sock.recv(4 - len(raw))
    (length,) = struct.unpack("<i", raw)
    data = b""
    while len(data) < length:
        data += sock.recv(length - len(data))
    req_id, ptype = struct.unpack("<ii", data[:8])
    return req_id, ptype, data[8:-2].decode("utf-8", errors="replace")


def run(commands):
    out = []
    with socket.create_connection((HOST, PORT), timeout=10) as s:
        s.sendall(_packet(1, 3, PASSWORD))
        req_id, _, _ = _recv(s)
        if req_id == -1:
            raise SystemExit("RCON 密碼錯誤")
        for i, cmd in enumerate(commands, start=2):
            s.sendall(_packet(i, 2, cmd))
            _, _, body = _recv(s)
            out.append((cmd, body))
    return out


def world_dir() -> Path:
    """依 server.properties 的 level-name 找到目前使用的世界資料夾。"""
    props = (ROOT / "server" / "server.properties").read_text(encoding="utf-8")
    for line in props.splitlines():
        if line.startswith("level-name="):
            return ROOT / "server" / line.split("=", 1)[1].strip()
    return ROOT / "server" / "world"


def deploy():
    src = ROOT / "datapack"
    dst = world_dir() / "datapacks"
    dst.mkdir(parents=True, exist_ok=True)
    for pack in src.iterdir():
        if pack.is_dir():
            target = dst / pack.name
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(pack, target)
            print(f"已部署資料包：{pack.name}")
    return run(["reload"])


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)
    results = deploy() if args == ["--deploy"] else run(args)
    for cmd, body in results:
        print(f"> {cmd}\n{body}" if body else f"> {cmd}")
