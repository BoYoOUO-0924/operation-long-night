# 由 tools/build_level.py 自動產生，請勿手動修改
scoreboard players set #stage ln 5
scoreboard players set #t ln 0
execute store result score #players ln if entity @a[gamemode=adventure]
execute if score #players ln matches ..0 run scoreboard players set #players ln 1
scoreboard players operation #budget ln = #players ln
scoreboard players remove #budget ln 1
scoreboard players operation #max ln = #budget ln
scoreboard players set #k ln 7
scoreboard players operation #budget ln *= #k ln
scoreboard players add #budget ln 20
scoreboard players set #k ln 2
scoreboard players operation #max ln *= #k ln
scoreboard players add #max ln 6
scoreboard players operation #total ln = #budget ln
scoreboard players set #sq ln 0
scoreboard players set #route ln 0
scoreboard players set #dt ln 400
scoreboard players set #pulse ln 0
scoreboard players set #evgen ln 0
scoreboard players set #final ln 0
scoreboard players set #tp ln 0
scoreboard players set #mort ln 0
execute store result bossbar ln:obj max run scoreboard players get #total ln
bossbar set ln:obj color red
