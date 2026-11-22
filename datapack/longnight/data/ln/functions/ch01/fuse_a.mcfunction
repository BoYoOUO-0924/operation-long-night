# 由 tools/build_ch01.py 自動產生，請勿手動修改
scoreboard players remove #fa ln 1
scoreboard players operation #fs ln = #fa ln
scoreboard players operation #fs ln /= #c20 ln
scoreboard players operation #fm ln = #fa ln
scoreboard players operation #fm ln %= #c20 ln
execute if score #fm ln matches 0 run playsound minecraft:block.note_block.bit master @a 28 129 1290 2 1.9
execute if score #fm ln matches 0 positioned 28 129 1290 run title @a[distance=..48] actionbar {"text": "", "font": "lnai:ui", "extra": [{"text": "北崖雷達  C4 引爆倒數 ", "color": "#F0A040"}, {"score": {"name": "#fs", "objective": "ln"}, "color": "white"}, {"text": " 秒", "color": "#F0A040"}]}
particle minecraft:dust 1 0 0 1.2 28.5 130.2 1290.5 0.1 0.1 0.1 0 2 force @a
execute if score #fa ln matches ..0 run function ln:ch01/boom_a
