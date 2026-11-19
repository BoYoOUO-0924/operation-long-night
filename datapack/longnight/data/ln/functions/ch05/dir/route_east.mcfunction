# 由 tools/build_level.py 自動產生，請勿手動修改
execute if score #comp ln matches 0 run summon tacznpcs:npc 172 250 962 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","rt_east"],ForgeData:{ln_side:"red",ln_slot:0,ln_hunt:16}}
execute if score #comp ln matches 0 run summon tacznpcs:npc 172 250 962 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","rt_east"],ForgeData:{ln_side:"red",ln_slot:1,ln_hunt:16}}
execute if score #comp ln matches 0 run summon tacznpcs:npc 172 250 962 {template:"red_support",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","rt_east"],ForgeData:{ln_side:"red",ln_slot:2,ln_hunt:16}}
execute if score #comp ln matches 0 if score #players ln matches 3.. run summon tacznpcs:npc 172 250 962 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","rt_east"],ForgeData:{ln_side:"red",ln_slot:3,ln_hunt:16}}
execute if score #comp ln matches 1 run summon tacznpcs:npc 172 250 962 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","rt_east"],ForgeData:{ln_side:"red",ln_slot:0,ln_hunt:16}}
execute if score #comp ln matches 1 run summon tacznpcs:npc 172 250 962 {template:"red_cqb",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","rt_east"],ForgeData:{ln_side:"red",ln_slot:1,ln_hunt:16}}
execute if score #comp ln matches 1 run summon tacznpcs:npc 172 250 962 {template:"red_cqb",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","rt_east"],ForgeData:{ln_side:"red",ln_slot:2,ln_hunt:16}}
execute if score #comp ln matches 1 if score #players ln matches 3.. run summon tacznpcs:npc 172 250 962 {template:"red_support",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","rt_east"],ForgeData:{ln_side:"red",ln_slot:3,ln_hunt:16}}
execute if score #comp ln matches 2 run summon tacznpcs:npc 172 250 962 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","rt_east"],ForgeData:{ln_side:"red",ln_slot:0,ln_hunt:16}}
execute if score #comp ln matches 2 run summon tacznpcs:npc 172 250 962 {template:"red_sniper",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","rt_east"],ForgeData:{ln_side:"red",ln_slot:1,ln_hunt:16}}
execute if score #comp ln matches 2 run summon tacznpcs:npc 172 250 962 {template:"red_support",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","rt_east"],ForgeData:{ln_side:"red",ln_slot:2,ln_hunt:16}}
execute if score #comp ln matches 2 if score #players ln matches 3.. run summon tacznpcs:npc 172 250 962 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","rt_east"],ForgeData:{ln_side:"red",ln_slot:3,ln_hunt:16}}
spreadplayers 172 962 1 6 false @e[tag=ln_new]
execute if score #flip ln matches 0 run tellraw @a [{"text": "[戰車] ", "color": "gold", "bold": true}, {"text": "東邊山坡，一組人摸上來了！", "color": "white"}]
execute if score #flip ln matches 0 run execute as @a at @s run playsound minecraft:ui.button.click master @s ~ ~ ~ 0.3 1.8
execute if score #flip ln matches 1 run tellraw @a [{"text": "[戰車] ", "color": "gold", "bold": true}, {"text": "車庫外面有動靜，東邊！", "color": "white"}]
execute if score #flip ln matches 1 run execute as @a at @s run playsound minecraft:ui.button.click master @s ~ ~ ~ 0.3 1.8
