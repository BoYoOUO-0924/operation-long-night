# 由 tools/build_level.py 自動產生，請勿手動修改
kill @e[tag=ln_enemy]
clear @a[gamemode=adventure]
function ln:ch05/loadout
effect give @a[gamemode=adventure] instant_health 1 9 true
tellraw @a {"text": "[長夜] 補給已重新發放。", "color": "gray", "font": "lnai:ui"}
execute if score #stage ln matches 2 run function ln:ch05/to_s2
execute if score #stage ln matches 3 run function ln:ch05/to_s3
execute if score #stage ln matches 4 run function ln:ch05/to_s4
execute if score #stage ln matches 5 run function ln:ch05/to_s5
execute if score #stage ln matches 7 run function ln:ch05/to_s7
