# 由 tools/build_level.py 自動產生，請勿手動修改
scoreboard players add #sq ln 1
scoreboard players operation #slot ln = #sq ln
scoreboard players operation #slot ln %= #c8 ln
scoreboard players operation #comp ln = #sq ln
scoreboard players operation #comp ln %= #c3 ln
scoreboard players operation #flip ln = #sq ln
scoreboard players operation #flip ln %= #c2 ln
execute if score #route ln matches 0 run function ln:ch05/dir/route_east
execute if score #route ln matches 1 run function ln:ch05/dir/route_north
execute if score #route ln matches 2 run function ln:ch05/dir/route_south
execute if score #route ln matches 3 run function ln:ch05/dir/route_east
execute if score #route ln matches 4 run function ln:ch05/dir/route_west
execute if score #route ln matches 5 run function ln:ch05/dir/route_northeast
execute if score #slot ln matches 0 run function ln:ch05/dir/name_0
execute if score #slot ln matches 1 run function ln:ch05/dir/name_1
execute if score #slot ln matches 2 run function ln:ch05/dir/name_2
execute if score #slot ln matches 3 run function ln:ch05/dir/name_3
execute if score #slot ln matches 4 run function ln:ch05/dir/name_4
execute if score #slot ln matches 5 run function ln:ch05/dir/name_5
execute if score #slot ln matches 6 run function ln:ch05/dir/name_6
execute if score #slot ln matches 7 run function ln:ch05/dir/name_7
execute store result score #n ln if entity @e[tag=ln_new]
scoreboard players operation #budget ln -= #n ln
tag @e[tag=ln_new] remove ln_new
scoreboard players add #route ln 1
execute if score #route ln matches 6.. run scoreboard players set #route ln 0
scoreboard players set #dt ln 0
