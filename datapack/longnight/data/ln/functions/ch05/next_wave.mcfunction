# 由 tools/build_level.py 自動產生，請勿手動修改
scoreboard players add #wave ln 1
scoreboard players set #stage ln 5
scoreboard players set #t ln 0
execute store result score #players ln if entity @a[gamemode=adventure]
execute if score #players ln matches ..0 run scoreboard players set #players ln 1
execute if score #wave ln matches 1 run function ln:ch05/wave/spawn1
execute if score #wave ln matches 2 run function ln:ch05/wave/spawn2
execute if score #wave ln matches 3 run function ln:ch05/wave/spawn3
