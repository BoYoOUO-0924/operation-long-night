# 由 tools/build_ch01.py 自動產生，請勿手動修改
execute if score #comp ln matches 0 run summon tacznpcs:npc 44 250 1360 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_gate_inside"],ForgeData:{ln_side:"red",ln_slot:0,ln_hunt:24}}
execute if score #comp ln matches 0 run summon tacznpcs:npc 44 250 1360 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_gate_inside"],ForgeData:{ln_side:"red",ln_slot:1,ln_hunt:24}}
execute if score #comp ln matches 0 run summon tacznpcs:npc 44 250 1360 {template:"red_support",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_gate_inside"],ForgeData:{ln_side:"red",ln_slot:2,ln_hunt:24}}
execute if score #comp ln matches 0 if score #players ln matches 3.. run summon tacznpcs:npc 44 250 1360 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_gate_inside"],ForgeData:{ln_side:"red",ln_slot:3,ln_hunt:24}}
execute if score #comp ln matches 1 run summon tacznpcs:npc 44 250 1360 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_gate_inside"],ForgeData:{ln_side:"red",ln_slot:0,ln_hunt:24}}
execute if score #comp ln matches 1 run summon tacznpcs:npc 44 250 1360 {template:"red_cqb",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_gate_inside"],ForgeData:{ln_side:"red",ln_slot:1,ln_hunt:24}}
execute if score #comp ln matches 1 run summon tacznpcs:npc 44 250 1360 {template:"red_cqb",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_gate_inside"],ForgeData:{ln_side:"red",ln_slot:2,ln_hunt:24}}
execute if score #comp ln matches 1 if score #players ln matches 3.. run summon tacznpcs:npc 44 250 1360 {template:"red_support",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_gate_inside"],ForgeData:{ln_side:"red",ln_slot:3,ln_hunt:24}}
execute if score #comp ln matches 2 run summon tacznpcs:npc 44 250 1360 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_gate_inside"],ForgeData:{ln_side:"red",ln_slot:0,ln_hunt:24}}
execute if score #comp ln matches 2 run summon tacznpcs:npc 44 250 1360 {template:"red_sniper",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_gate_inside"],ForgeData:{ln_side:"red",ln_slot:1,ln_hunt:24}}
execute if score #comp ln matches 2 run summon tacznpcs:npc 44 250 1360 {template:"red_support",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_gate_inside"],ForgeData:{ln_side:"red",ln_slot:2,ln_hunt:24}}
execute if score #comp ln matches 2 if score #players ln matches 3.. run summon tacznpcs:npc 44 250 1360 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_dress","rt_gate_inside"],ForgeData:{ln_side:"red",ln_slot:3,ln_hunt:24}}
spreadplayers 44 1360 1 5 false @e[tag=ln_new]
schedule function ln:ch05/dress 2t replace
team join ln_red @e[tag=ln_new]
execute if score #flip ln matches 0 if score #callout ln matches 1 run lnhud say @a E0B050 85 "戰車" 大門裡面湧出來了!
execute if score #flip ln matches 1 if score #callout ln matches 1 run lnhud say @a E0B050 70 "戰車" 門內有敵人!
scoreboard players add #comp ln 1
execute if score #comp ln matches 3.. run scoreboard players set #comp ln 0
scoreboard players add #flip ln 1
execute if score #flip ln matches 2.. run scoreboard players set #flip ln 0
tag @e[tag=ln_new] add ln_fresh
tag @e[tag=ln_new] remove ln_new
