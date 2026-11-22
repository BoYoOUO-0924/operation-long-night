# 由 tools/build_ch01.py 自動產生，請勿手動修改
function ln:ch01/dlg/beach
execute if score #light ln matches 0 run function ln:ch01/sl2/tick
execute if score #t ln matches 20.. positioned 78 85 1400 if entity @a[distance=..6] run lnhud waypoint @a 73 96 1406
execute if score #scan ln matches 0 positioned 73 96 1406 if entity @a[gamemode=adventure,distance=..30] run function ln:ch01/scan_first
execute if score #scan ln matches 1.. run scoreboard players add #scan ln 1
execute if score #scan ln matches 400.. run function ln:ch01/scan
execute as @e[tag=c1_cable] run function ln:ch01/hit_cable
execute if score #light ln matches 0 if score #cable ln matches 3.. run function ln:ch01/light_out
execute as @e[tag=c1_barrels] run function ln:ch01/hit_barrels
execute if score #aa ln matches 0 if score #bar ln matches 2.. run function ln:ch01/aa_down
execute as @e[tag=c1_aa_btn] if data entity @s interaction run function ln:ch01/aa_plant
execute if score #aaf ln matches 1.. run scoreboard players remove #aaf ln 1
execute if score #aaf ln matches 1.. run particle minecraft:dust 1 0 0 1.5 56 93 1428 0.2 0.2 0.2 0 2 force @a
execute if score #aa ln matches 0 if score #aaf ln matches 1 run function ln:ch01/aa_down
execute if score #light ln matches 1 if score #aa ln matches 1 run function ln:ch01/to_s3
