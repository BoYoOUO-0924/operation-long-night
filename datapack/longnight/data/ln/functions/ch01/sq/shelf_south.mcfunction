# 由 tools/build_ch01.py 自動產生，請勿手動修改
execute if score #comp ln matches 0 run summon tacznpcs:npc 60 250 1446 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_shelf_south"],ForgeData:{ln_side:"red",ln_slot:0,ln_hunt:24}}
execute if score #comp ln matches 0 run summon tacznpcs:npc 60 250 1446 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_shelf_south"],ForgeData:{ln_side:"red",ln_slot:1,ln_hunt:24}}
execute if score #comp ln matches 0 run summon tacznpcs:npc 60 250 1446 {template:"red_support",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_shelf_south"],ForgeData:{ln_side:"red",ln_slot:2,ln_hunt:24}}
execute if score #comp ln matches 0 if score #players ln matches 3.. run summon tacznpcs:npc 60 250 1446 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_shelf_south"],ForgeData:{ln_side:"red",ln_slot:3,ln_hunt:24}}
execute if score #comp ln matches 1 run summon tacznpcs:npc 60 250 1446 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_shelf_south"],ForgeData:{ln_side:"red",ln_slot:0,ln_hunt:24}}
execute if score #comp ln matches 1 run summon tacznpcs:npc 60 250 1446 {template:"red_cqb",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_shelf_south"],ForgeData:{ln_side:"red",ln_slot:1,ln_hunt:24}}
execute if score #comp ln matches 1 run summon tacznpcs:npc 60 250 1446 {template:"red_cqb",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_shelf_south"],ForgeData:{ln_side:"red",ln_slot:2,ln_hunt:24}}
execute if score #comp ln matches 1 if score #players ln matches 3.. run summon tacznpcs:npc 60 250 1446 {template:"red_support",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_shelf_south"],ForgeData:{ln_side:"red",ln_slot:3,ln_hunt:24}}
execute if score #comp ln matches 2 run summon tacznpcs:npc 60 250 1446 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_shelf_south"],ForgeData:{ln_side:"red",ln_slot:0,ln_hunt:24}}
execute if score #comp ln matches 2 run summon tacznpcs:npc 60 250 1446 {template:"red_sniper",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_shelf_south"],ForgeData:{ln_side:"red",ln_slot:1,ln_hunt:24}}
execute if score #comp ln matches 2 run summon tacznpcs:npc 60 250 1446 {template:"red_support",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_shelf_south"],ForgeData:{ln_side:"red",ln_slot:2,ln_hunt:24}}
execute if score #comp ln matches 2 if score #players ln matches 3.. run summon tacznpcs:npc 60 250 1446 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_shelf_south"],ForgeData:{ln_side:"red",ln_slot:3,ln_hunt:24}}
spreadplayers 60 1446 1 5 false @e[tag=ln_new]
schedule function ln:ch05/dress 2t replace
team join ln_red @e[tag=ln_new]
execute if score #flip ln matches 0 if score #callout ln matches 1 run lnhud say @a 7FC8D8 85 "白鴉" 南邊岩棚有人上來!
execute if score #flip ln matches 1 if score #callout ln matches 1 run lnhud say @a 7FC8D8 85 "白鴉" 南側, 一組敵人!
scoreboard players add #comp ln 1
execute if score #comp ln matches 3.. run scoreboard players set #comp ln 0
scoreboard players add #flip ln 1
execute if score #flip ln matches 2.. run scoreboard players set #flip ln 0
tag @e[tag=ln_new] add ln_fresh
tag @e[tag=ln_new] remove ln_new
