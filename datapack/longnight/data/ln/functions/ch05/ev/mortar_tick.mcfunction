# 由 tools/build_level.py 自動產生，請勿手動修改
scoreboard players add #mt ln 1
execute if score #mt ln matches 80 if score #mort ln matches 1.. as @r[gamemode=adventure] at @s run summon marker ~ ~ ~ {Tags:["ln","ln_mortar","ln_newm"]}
execute as @e[tag=ln_newm] at @s run spreadplayers ~ ~ 0 8 false @s
tag @e[tag=ln_newm] remove ln_newm
execute if score #mt ln matches 80 if score #mort ln matches 1.. run scoreboard players remove #mort ln 1
execute if score #mt ln matches 80 run scoreboard players set #mt ln 0
scoreboard players add @e[tag=ln_mortar] ln_age 1
execute as @e[tag=ln_mortar] at @s run particle minecraft:dust 1 0 0 2 ~ ~0.2 ~ 1.5 0 1.5 0 6 force @a
execute as @e[tag=ln_mortar,scores={ln_age=10}] at @s run playsound lnai:sfx.mortar_launch master @a ~ ~ ~ 3 1
execute as @e[tag=ln_mortar,scores={ln_age=30}] at @s run playsound lnai:sfx.mortar_whistle master @a ~ ~8 ~ 3 1
execute as @e[tag=ln_mortar,scores={ln_age=50}] at @s run summon superbwarfare:mortar_shell ~ ~40 ~ {Motion:[0.0d,-2.0d,0.0d]}
kill @e[tag=ln_mortar,scores={ln_age=50..}]
