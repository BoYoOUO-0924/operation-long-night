# 由 tools/build_level.py 自動產生，請勿手動修改
execute if score #comp ln matches 0 run summon tacznpcs:npc 100 250 1018 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_south"],ForgeData:{ln_side:"red",ln_slot:0,ln_hunt:16}}
execute if score #comp ln matches 0 run summon tacznpcs:npc 100 250 1018 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_south"],ForgeData:{ln_side:"red",ln_slot:1,ln_hunt:16}}
execute if score #comp ln matches 0 run summon tacznpcs:npc 100 250 1018 {template:"red_support",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_south"],ForgeData:{ln_side:"red",ln_slot:2,ln_hunt:16}}
execute if score #comp ln matches 0 if score #players ln matches 3.. run summon tacznpcs:npc 100 250 1018 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_south"],ForgeData:{ln_side:"red",ln_slot:3,ln_hunt:16}}
execute if score #comp ln matches 1 run summon tacznpcs:npc 100 250 1018 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_south"],ForgeData:{ln_side:"red",ln_slot:0,ln_hunt:16}}
execute if score #comp ln matches 1 run summon tacznpcs:npc 100 250 1018 {template:"red_cqb",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_south"],ForgeData:{ln_side:"red",ln_slot:1,ln_hunt:16}}
execute if score #comp ln matches 1 run summon tacznpcs:npc 100 250 1018 {template:"red_cqb",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_south"],ForgeData:{ln_side:"red",ln_slot:2,ln_hunt:16}}
execute if score #comp ln matches 1 if score #players ln matches 3.. run summon tacznpcs:npc 100 250 1018 {template:"red_support",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_south"],ForgeData:{ln_side:"red",ln_slot:3,ln_hunt:16}}
execute if score #comp ln matches 2 run summon tacznpcs:npc 100 250 1018 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_south"],ForgeData:{ln_side:"red",ln_slot:0,ln_hunt:16}}
execute if score #comp ln matches 2 run summon tacznpcs:npc 100 250 1018 {template:"red_sniper",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_south"],ForgeData:{ln_side:"red",ln_slot:1,ln_hunt:16}}
execute if score #comp ln matches 2 run summon tacznpcs:npc 100 250 1018 {template:"red_support",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_south"],ForgeData:{ln_side:"red",ln_slot:2,ln_hunt:16}}
execute if score #comp ln matches 2 if score #players ln matches 3.. run summon tacznpcs:npc 100 250 1018 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_south"],ForgeData:{ln_side:"red",ln_slot:3,ln_hunt:16}}
spreadplayers 100 1018 1 6 false @e[tag=ln_new]
schedule function ln:ch05/dress 2t replace
execute if score #flip ln matches 0 run tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "[白鴉] ", "color": "aqua", "bold": true}, {"text": "南邊高地有人, 小心觀測場那邊! ", "color": "white"}]}
execute if score #flip ln matches 0 run execute as @a at @s run playsound minecraft:ui.button.click master @s ~ ~ ~ 0.3 1.8
execute if score #flip ln matches 1 run tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "[白鴉] ", "color": "aqua", "bold": true}, {"text": "南側斜坡, 一整組人壓下來了! ", "color": "white"}]}
execute if score #flip ln matches 1 run execute as @a at @s run playsound minecraft:ui.button.click master @s ~ ~ ~ 0.3 1.8
