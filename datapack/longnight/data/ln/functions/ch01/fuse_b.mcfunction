# 由 tools/build_ch01.py 自動產生，請勿手動修改
scoreboard players remove #fb ln 1
scoreboard players operation #fs ln = #fb ln
scoreboard players operation #fs ln /= #c20 ln
scoreboard players operation #fm ln = #fb ln
scoreboard players operation #fm ln %= #c20 ln
execute if score #fm ln matches 0 run playsound minecraft:block.note_block.bit master @a 22 127 1324 2 1.9
execute if score #fm ln matches 0 positioned 22 127 1324 run title @a[distance=..48] actionbar {"text": "", "font": "lnai:ui", "extra": [{"text": "中央雷達  C4 引爆倒數 ", "color": "#F0A040"}, {"score": {"name": "#fs", "objective": "ln"}, "color": "white"}, {"text": " 秒", "color": "#F0A040"}]}
particle minecraft:dust 1 0 0 1.2 22.5 128.2 1324.5 0.1 0.1 0.1 0 2 force @a
execute if score #fb ln matches ..0 run function ln:ch01/boom_b
