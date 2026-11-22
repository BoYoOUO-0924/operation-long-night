# 由 tools/build_ch01.py 自動產生，請勿手動修改
scoreboard players set #stage ln 4
scoreboard players set #t ln 0
function ln:ch01/arm
execute unless score #count ln matches 0.. run scoreboard players set #count ln 0
execute unless score #tl ln matches 1.. run scoreboard players set #tl ln 14400
execute store result score #players ln if entity @a[gamemode=adventure]
execute if score #players ln matches ..0 run scoreboard players set #players ln 1
scoreboard players operation #max ln = #players ln
scoreboard players set #k ln 3
scoreboard players operation #max ln *= #k ln
scoreboard players add #max ln 5
scoreboard players set #dt ln 300
scoreboard players set #route ln 0
execute unless score #rc ln matches 2 unless entity @e[tag=c1_sniper] run summon tacznpcs:npc 98 126 1464 {template:"red_sniper",PersistenceRequired:1b,Tags:["ln","ln_enemy","c1_sniper","ln_dress"],ForgeData:{ln_side:"red",ln_hunt:64,ln_wp:[I;98,126,1464],ln_wpr:1}}
team join ln_red @e[tag=c1_sniper]
schedule function ln:ch05/dress 2t replace
bossbar set ln:obj max 14400
bossbar set ln:obj color red
lnhud waypoint @a clear
execute unless score #rc ln matches 2 run lnhud waypoint @a 101 126 1462
execute unless score #rb ln matches 2 run lnhud waypoint @a 22 127 1324
execute unless score #ra ln matches 2 run lnhud waypoint @a 28 129 1290
lnhud music @a ch05_battle 40
execute unless score #near_b ln matches 1 run scoreboard players set #near_b ln 0
execute unless score #near_c ln matches 1 run scoreboard players set #near_c ln 0
