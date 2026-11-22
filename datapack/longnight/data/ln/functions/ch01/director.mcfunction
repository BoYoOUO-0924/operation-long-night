# 由 tools/build_ch01.py 自動產生，請勿手動修改
scoreboard players add #dt ln 1
execute if score #dt ln matches 500.. if score #alive ln < #max ln if score #route ln matches 0 run function ln:ch01/sq/shelf_south
execute if score #dt ln matches 500.. if score #alive ln < #max ln if score #route ln matches 1 run function ln:ch01/sq/plateau_west
execute if score #dt ln matches 500.. if score #alive ln < #max ln if score #route ln matches 2 run function ln:ch01/sq/plateau_north
execute if score #dt ln matches 500.. if score #alive ln < #max ln if score #route ln matches 3 run function ln:ch01/sq/gate_inside
execute if score #dt ln matches 500.. if score #alive ln < #max ln if score #route ln matches 4 run function ln:ch01/sq/south_cape
execute as @e[tag=ln_fresh] run data merge entity @s {ForgeData:{ln_hunt:64}}
tag @e[tag=ln_fresh] remove ln_fresh
execute if score #dt ln matches 500.. if score #alive ln < #max ln run scoreboard players add #route ln 1
execute if score #route ln matches 5.. run scoreboard players set #route ln 0
execute if score #dt ln matches 500.. run scoreboard players set #dt ln 0
