# 由 tools/build_ch01.py 自動產生，請勿手動修改
kill @e[tag=ln_enemy]
clear @a[gamemode=adventure]
function ln:ch01/loadout
effect give @a[gamemode=adventure] instant_health 1 9 true
tellraw @a {"text": "[長夜] 補給已重新發放。", "color": "gray", "font": "lnai:ui"}
execute if score #stage ln matches 2 run tp @a[gamemode=adventure] 82 64 1400
execute if score #stage ln matches 2 run function ln:ch01/to_s2
execute if score #stage ln matches 3 run tp @a[gamemode=adventure] 49 110 1377
execute if score #stage ln matches 3 run function ln:ch01/to_s3
execute if score #stage ln matches 4 run tp @a[gamemode=adventure] 49 110 1369
execute if score #stage ln matches 4 if score #tl ln matches ..3600 run scoreboard players set #tl ln 3600
execute if score #stage ln matches 4 run function ln:ch01/to_s4
