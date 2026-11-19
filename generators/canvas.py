"""方塊畫布：在 Python 裡「畫」建築，再輸出成 Minecraft 指令（相對座標 ~x ~y ~z）。

輸出的 mcfunction 要用 `execute positioned <x> <y> <z> run function ...` 執行，
原點 (0,0,0) 就是建築的西北角地板。
"""
import random


class Canvas:
    def __init__(self, seed=7):
        self.blocks = {}          # (x,y,z) -> block state 字串
        self.oy = 0               # 目前結構的高度偏移（讓每棟建築貼合自己的地面）
        self.pre = []             # 建築前要先跑的指令（清空、地基）
        self.post = []            # 建築後的指令（告示牌、實體等）
        self.rng = random.Random(seed)

    # ---- 基本操作 -------------------------------------------------
    def set(self, x, y, z, block):
        self.blocks[(x, y + self.oy, z)] = block

    def get(self, x, y, z):
        return self.blocks.get((x, y + self.oy, z))

    def box(self, x1, y1, z1, x2, y2, z2, block):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    self.set(x, y, z, block() if callable(block) else block)

    def hollow(self, x1, y1, z1, x2, y2, z2, block):
        """只畫外殼（牆、地板、天花板）。"""
        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                for z in range(z1, z2 + 1):
                    if x in (x1, x2) or y in (y1, y2) or z in (z1, z2):
                        self.set(x, y, z, block() if callable(block) else block)

    def walls(self, x1, y1, z1, x2, y2, z2, block):
        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                for z in range(z1, z2 + 1):
                    if x in (x1, x2) or z in (z1, z2):
                        self.set(x, y, z, block() if callable(block) else block)

    def pick(self, weighted):
        """weighted: [(block, 權重), ...] → 回傳一個隨機挑選的函式，用來做風化效果。"""
        blocks, weights = zip(*weighted)
        return lambda: self.rng.choices(blocks, weights)[0]

    def chance(self, p):
        return self.rng.random() < p

    # ---- 輸出 -----------------------------------------------------
    def commands(self):
        out = list(self.pre)
        # 依 (y, z) 分組，x 方向連續且相同的方塊合併成 fill
        keys = sorted(self.blocks, key=lambda k: (k[1], k[2], k[0]))
        i = 0
        while i < len(keys):
            x, y, z = keys[i]
            b = self.blocks[keys[i]]
            j = i
            while (j + 1 < len(keys) and keys[j + 1] == (keys[j][0] + 1, y, z)
                   and self.blocks[keys[j + 1]] == b):
                j += 1
            x2 = keys[j][0]
            if x2 == x:
                out.append(f"setblock ~{x} ~{y} ~{z} {b}")
            else:
                out.append(f"fill ~{x} ~{y} ~{z} ~{x2} ~{y} ~{z} {b}")
            i = j + 1
        out += self.post
        return out

    def write(self, path, header=""):
        cmds = self.commands()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text((header + "\n" if header else "") + "\n".join(cmds) + "\n", encoding="utf-8")
        return len(cmds)
