# 由 tools/build_ch01.py 自動產生，請勿手動修改
data remove entity @s interaction
execute if score #aaf ln matches 0 if score #aa ln matches 0 run scoreboard players set #aaf ln 100
kill @e[tag=c1_aa_lbl]
playsound minecraft:block.note_block.bit master @a 56 93 1428 2 1.6
title @a actionbar {"text": "C4 已安裝，5 秒後引爆——快離開！", "color": "#F0A040", "font": "lnai:ui"}
