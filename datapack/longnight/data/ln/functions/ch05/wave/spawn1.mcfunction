# 由 tools/build_level.py 自動產生，請勿手動修改
summon tacznpcs:npc 182 250 956 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_new_east"]}
summon tacznpcs:npc 182 250 956 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_new_east"]}
summon tacznpcs:npc 182 250 956 {template:"red_cqb",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_new_east"]}
summon tacznpcs:npc 182 250 956 {template:"red_support",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_new","ln_new_east"]}
execute if score #players ln matches 2.. run function ln:ch05/wave/extra1
execute if score #players ln matches 3.. run function ln:ch05/wave/extra1
execute if score #players ln matches 4.. run function ln:ch05/wave/extra1
execute if entity @e[tag=ln_new_east] run spreadplayers 182 956 2 8 false @e[tag=ln_new_east]
tag @e[tag=ln_new_east] remove ln_new_east
tag @e[tag=ln_new] remove ln_new
execute store result bossbar ln:obj max if entity @e[tag=ln_enemy]
function ln:ch05/dlg/wave1
