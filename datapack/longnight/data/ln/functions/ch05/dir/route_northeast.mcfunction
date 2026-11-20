# 由 tools/build_level.py 自動產生，請勿手動修改
execute if score #comp ln matches 0 run summon tacznpcs:npc 150 250 928 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_northeast"],ForgeData:{ln_side:"red",ln_slot:0,ln_hunt:16}}
execute if score #comp ln matches 0 run summon tacznpcs:npc 150 250 928 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_northeast"],ForgeData:{ln_side:"red",ln_slot:1,ln_hunt:16}}
execute if score #comp ln matches 0 run summon tacznpcs:npc 150 250 928 {template:"red_support",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_northeast"],ForgeData:{ln_side:"red",ln_slot:2,ln_hunt:16}}
execute if score #comp ln matches 0 if score #players ln matches 3.. run summon tacznpcs:npc 150 250 928 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_northeast"],ForgeData:{ln_side:"red",ln_slot:3,ln_hunt:16}}
execute if score #comp ln matches 1 run summon tacznpcs:npc 150 250 928 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_northeast"],ForgeData:{ln_side:"red",ln_slot:0,ln_hunt:16}}
execute if score #comp ln matches 1 run summon tacznpcs:npc 150 250 928 {template:"red_cqb",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_northeast"],ForgeData:{ln_side:"red",ln_slot:1,ln_hunt:16}}
execute if score #comp ln matches 1 run summon tacznpcs:npc 150 250 928 {template:"red_cqb",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_northeast"],ForgeData:{ln_side:"red",ln_slot:2,ln_hunt:16}}
execute if score #comp ln matches 1 if score #players ln matches 3.. run summon tacznpcs:npc 150 250 928 {template:"red_support",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_northeast"],ForgeData:{ln_side:"red",ln_slot:3,ln_hunt:16}}
execute if score #comp ln matches 2 run summon tacznpcs:npc 150 250 928 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_northeast"],ForgeData:{ln_side:"red",ln_slot:0,ln_hunt:16}}
execute if score #comp ln matches 2 run summon tacznpcs:npc 150 250 928 {template:"red_sniper",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_northeast"],ForgeData:{ln_side:"red",ln_slot:1,ln_hunt:16}}
execute if score #comp ln matches 2 run summon tacznpcs:npc 150 250 928 {template:"red_support",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_northeast"],ForgeData:{ln_side:"red",ln_slot:2,ln_hunt:16}}
execute if score #comp ln matches 2 if score #players ln matches 3.. run summon tacznpcs:npc 150 250 928 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_northeast"],ForgeData:{ln_side:"red",ln_slot:3,ln_hunt:16}}
spreadplayers 150 928 1 6 false @e[tag=ln_new]
schedule function ln:ch05/dress 2t replace
execute if score #flip ln matches 0 run lnhud say @a 7FC8D8 115 "白鴉" 東北角! 天線塔那邊有一組! 
execute if score #flip ln matches 0 run execute as @a at @s run playsound minecraft:ui.button.click master @s ~ ~ ~ 0.3 1.8
execute if score #flip ln matches 1 run lnhud say @a 7FC8D8 100 "白鴉" 他們從東北包夾過來了! 
execute if score #flip ln matches 1 run execute as @a at @s run playsound minecraft:ui.button.click master @s ~ ~ ~ 0.3 1.8
