# 由 tools/build_ch01.py 自動產生，請勿手動修改
execute unless score #fail ln matches 1.. run function ln:ch01/dlg/radars
scoreboard players remove #tl ln 1
execute store result bossbar ln:obj value run scoreboard players get #tl ln
scoreboard players operation #ss ln = #tl ln
scoreboard players operation #ss ln /= #c20 ln
scoreboard players operation #mm ln = #ss ln
scoreboard players set #k ln 60
scoreboard players operation #mm ln /= #k ln
scoreboard players operation #ss ln %= #k ln
execute if score #ss ln matches 10.. run bossbar set ln:obj name {"text": "", "font": "lnai:ui", "extra": [{"text": "艦隊進入射程倒數  ", "color": "red"}, {"score": {"name": "#mm", "objective": "ln"}, "color": "white"}, {"text": ":", "color": "white"}, {"score": {"name": "#ss", "objective": "ln"}, "color": "white"}, {"text": "　雷達 ", "color": "red"}, {"score": {"name": "#count", "objective": "ln"}, "color": "white"}, {"text": "/3", "color": "white"}]}
execute if score #ss ln matches ..9 run bossbar set ln:obj name {"text": "", "font": "lnai:ui", "extra": [{"text": "艦隊進入射程倒數  ", "color": "red"}, {"score": {"name": "#mm", "objective": "ln"}, "color": "white"}, {"text": ":0", "color": "white"}, {"score": {"name": "#ss", "objective": "ln"}, "color": "white"}, {"text": "　雷達 ", "color": "red"}, {"score": {"name": "#count", "objective": "ln"}, "color": "white"}, {"text": "/3", "color": "white"}]}
execute if score #tl ln matches 3600 run function ln:ch01/evdlg/evt_3min
execute if score #tl ln matches ..0 if score #count ln matches ..2 run function ln:ch01/fail
execute store result score #alive ln if entity @e[tag=ln_enemy]
function ln:ch01/director
execute if score #near_b ln matches 0 positioned 22 127 1322 if entity @a[gamemode=adventure,distance=..30] run function ln:ch01/near_b
execute if score #near_c ln matches 0 positioned 96 104 1462 if entity @a[gamemode=adventure,distance=..40] run function ln:ch01/near_c
execute as @e[tag=c1_c4a] if data entity @s interaction run function ln:ch01/plant_a
execute as @e[tag=c1_c4b] if data entity @s interaction run function ln:ch01/plant_b
execute as @e[tag=c1_c4c] if data entity @s interaction run function ln:ch01/plant_c
execute if score #ra ln matches 1 run function ln:ch01/fuse_a
execute if score #rb ln matches 1 run function ln:ch01/fuse_b
execute if score #rc ln matches 1 run function ln:ch01/fuse_c
execute if score #count ln matches 3.. run scoreboard players add #endt ln 1
execute if score #endt ln matches 100.. run function ln:ch01/to_s5
