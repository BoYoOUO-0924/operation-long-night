# 由 tools/build_ch01.py 自動產生，請勿手動修改
function ln:ch01/dlg/drop
function ln:ch01/chute
function ln:ch01/sl1/tick
execute as @e[tag=c1_beacon] at @s run particle minecraft:dust 0.2 1 0.3 2 ~ ~0.5 ~ 0.2 0.6 0.2 0 4 force @a
execute as @e[tag=c1_beacon] at @s run particle minecraft:end_rod ~ ~1 ~ 0.1 2 0.1 0.01 2 force @a
execute as @a at @s run particle minecraft:rain ~ ~3 ~ 8 3 8 0 20 normal @s
execute unless entity @a[tag=c1_chute] run function ln:ch01/to_s2
execute if score #landed ln matches 1.. run scoreboard players add #c1lt ln 1
execute if score #c1lt ln matches 400.. run function ln:ch01/force_land
execute if score #t ln matches 2400.. run function ln:ch01/force_land
