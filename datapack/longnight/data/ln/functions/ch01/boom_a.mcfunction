# 由 tools/build_ch01.py 自動產生，請勿手動修改
scoreboard players set #ra ln 2
kill @e[tag=c1_c4a]
kill @e[tag=c1_c4vis_a]
kill @e[tag=c1_lbla]
particle minecraft:explosion_emitter 32 133 1290 1 1 1 0 2 force @a
particle minecraft:large_smoke 32 133 1290 1.5 1.5 1.5 0.05 40 force @a
particle minecraft:lava 32 133 1290 1 1 1 0 20 force @a
playsound lnai:sfx.boom master @a 32 133 1290 6 0.9
playsound minecraft:entity.generic.explode master @a 32 133 1290 4 0.7
particle minecraft:explosion 32 142 1290 1 1 1 0 6 force @a
particle minecraft:large_smoke 32 142 1290 1.5 1.5 1.5 0.05 40 force @a
particle minecraft:lava 32 142 1290 1 1 1 0 20 force @a
playsound lnai:sfx.boom master @a 32 142 1290 6 0.9
playsound minecraft:entity.generic.explode master @a 32 142 1290 4 0.7
fill 28 129 1285 37 145 1295 air
fill 29 129 1287 35 129 1288 smooth_quartz_slab
setblock 30 129 1293 iron_bars
setblock 31 129 1292 campfire[lit=true]
setblock 32 129 1290 campfire[lit=true]
execute positioned 32 129 1290 run kill @e[tag=ln_enemy,distance=..6]
lnhud tint @a 70FFE0B0 20 flash
scoreboard players add #count ln 1
function ln:ch01/evdlg/evt_boom_a
execute if score #count ln matches 1 run function ln:ch01/evdlg/evt_count_1
execute if score #count ln matches 2 run function ln:ch01/evdlg/evt_count_2
execute if score #count ln matches 3 run function ln:ch01/evdlg/evt_count_3
lnhud waypoint @a clear
execute unless score #rc ln matches 2 run lnhud waypoint @a 101 126 1462
execute unless score #rb ln matches 2 run lnhud waypoint @a 22 127 1324
execute unless score #ra ln matches 2 run lnhud waypoint @a 28 129 1290
