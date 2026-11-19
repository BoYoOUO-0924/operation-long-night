# 由 tools/build_level.py 自動產生，請勿手動修改
summon tacznpcs:npc 166 250 963 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_new_east"]}
summon tacznpcs:npc 166 250 963 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_new_east"]}
summon tacznpcs:npc 166 250 963 {template:"red_support",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_new_east"]}
summon tacznpcs:npc 166 250 963 {template:"red_cqb",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_new_east"]}
summon tacznpcs:npc 50 250 965 {template:"red_sniper",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_new_west"]}
summon tacznpcs:npc 50 250 965 {template:"red_sniper",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_new_west"]}
summon tacznpcs:npc 50 250 965 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_new_west"]}
summon tacznpcs:npc 102 250 919 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_new_north"]}
summon tacznpcs:npc 102 250 919 {template:"red_cqb",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_new_north"]}
summon tacznpcs:npc 102 250 919 {template:"red_support",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_new_north"]}
execute if score #players ln matches 2.. run function ln:ch05/wave/extra3
execute if score #players ln matches 3.. run function ln:ch05/wave/extra3
execute if score #players ln matches 4.. run function ln:ch05/wave/extra3
execute if entity @e[tag=ln_new_east] run spreadplayers 166 963 2 8 false @e[tag=ln_new_east]
tag @e[tag=ln_new_east] remove ln_new_east
execute if entity @e[tag=ln_new_north] run spreadplayers 102 919 2 8 false @e[tag=ln_new_north]
tag @e[tag=ln_new_north] remove ln_new_north
execute if entity @e[tag=ln_new_west] run spreadplayers 50 965 2 8 false @e[tag=ln_new_west]
tag @e[tag=ln_new_west] remove ln_new_west
tag @e[tag=ln_new] remove ln_new
execute store result bossbar ln:obj max if entity @e[tag=ln_enemy]
function ln:ch05/dlg/wave3
