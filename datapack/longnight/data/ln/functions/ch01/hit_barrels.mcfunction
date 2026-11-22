# 由 tools/build_ch01.py 自動產生，請勿手動修改
execute store result score #h ln run data get entity @s Health
execute if score #h ln matches ..999 run scoreboard players add #bar ln 1
execute if score #h ln matches ..999 at @s run particle minecraft:lava ~ ~0.5 ~ 0.3 0.3 0.3 0.2 15 force @a
execute if score #h ln matches ..999 at @s run playsound minecraft:block.anvil.land master @a ~ ~ ~ 0.6 1.8
execute if score #h ln matches ..999 run data modify entity @s Health set value 1000f
