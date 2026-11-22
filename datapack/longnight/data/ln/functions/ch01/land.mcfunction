# 由 tools/build_ch01.py 自動產生，請勿手動修改
tag @s remove c1_chute
effect clear @s slow_falling
execute if score @s ln_pid matches 1 run kill @e[tag=c1_chute_1]
execute if score @s ln_pid matches 2 run kill @e[tag=c1_chute_2]
execute if score @s ln_pid matches 3 run kill @e[tag=c1_chute_3]
execute if score @s ln_pid matches 4 run kill @e[tag=c1_chute_4]
playsound minecraft:item.armor.equip_leather master @a ~ ~ ~ 1 0.7
particle minecraft:poof ~ ~0.2 ~ 0.6 0.1 0.6 0.02 12
scoreboard players add #landed ln 1
