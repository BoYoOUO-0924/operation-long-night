# 由 tools/build_ch01.py 自動產生，請勿手動修改
setblock 122 299 1406 air
setblock 126 299 1414 air
setblock 122 299 1422 air
setblock 128 299 1428 air
execute if entity @a[scores={ln_pid=1}] run summon block_display 122 300 1406 {Tags:["ln","c1_chute_e","c1_chute_1"],view_range:3f,block_state:{Name:"minecraft:green_terracotta"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[-1.6f,2.7f,-1.2f],scale:[3.2f,0.35f,2.4f]}}
execute if entity @a[scores={ln_pid=2}] run summon block_display 126 300 1414 {Tags:["ln","c1_chute_e","c1_chute_2"],view_range:3f,block_state:{Name:"minecraft:green_terracotta"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[-1.6f,2.7f,-1.2f],scale:[3.2f,0.35f,2.4f]}}
execute if entity @a[scores={ln_pid=3}] run summon block_display 122 300 1422 {Tags:["ln","c1_chute_e","c1_chute_3"],view_range:3f,block_state:{Name:"minecraft:green_terracotta"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[-1.6f,2.7f,-1.2f],scale:[3.2f,0.35f,2.4f]}}
execute if entity @a[scores={ln_pid=4}] run summon block_display 128 300 1428 {Tags:["ln","c1_chute_e","c1_chute_4"],view_range:3f,block_state:{Name:"minecraft:green_terracotta"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[-1.6f,2.7f,-1.2f],scale:[3.2f,0.35f,2.4f]}}
tag @a[gamemode=adventure] add c1_chute
effect give @a[gamemode=adventure] slow_falling infinite 0 true
effect give @e[tag=ln_ally] slow_falling 120 0 true
effect give @e[tag=ln_ally] glowing infinite 0 true
kill @e[tag=c1_bcn]
scoreboard players set #stage ln 1
scoreboard players set #t ln 0
