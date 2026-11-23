# 由 tools/build_ch01.py 自動產生，請勿手動修改
scoreboard players set #rc ln 2
kill @e[tag=c1_c4c]
kill @e[tag=c1_c4vis_c]
kill @e[tag=c1_lblc]
particle minecraft:explosion_emitter 102 135 1462 1 1 1 0 2 force @a
particle minecraft:large_smoke 102 135 1462 1.5 1.5 1.5 0.05 40 force @a
particle minecraft:lava 102 135 1462 1 1 1 0 20 force @a
playsound lnai:sfx.boom master @a 102 135 1462 6 0.9
playsound minecraft:entity.generic.explode master @a 102 135 1462 4 0.7
particle minecraft:explosion 102 140 1462 1 1 1 0 6 force @a
particle minecraft:large_smoke 102 140 1462 1.5 1.5 1.5 0.05 40 force @a
particle minecraft:lava 102 140 1462 1 1 1 0 20 force @a
playsound lnai:sfx.boom master @a 102 140 1462 6 0.9
playsound minecraft:entity.generic.explode master @a 102 140 1462 4 0.7
fill 98 131 1457 107 143 1467 air
fill 99 131 1459 105 131 1460 smooth_quartz_slab
setblock 100 131 1465 iron_bars
setblock 101 131 1464 campfire[lit=true]
setblock 102 131 1462 campfire[lit=true]
execute positioned 102 131 1462 run kill @e[tag=ln_enemy,distance=..6]
lnhud tint @a 70FFE0B0 20 flash
scoreboard players add #count ln 1
function ln:ch01/evdlg/evt_boom_c
execute if score #count ln matches 1 run function ln:ch01/evdlg/evt_count_1
execute if score #count ln matches 2 run function ln:ch01/evdlg/evt_count_2
execute if score #count ln matches 3 run function ln:ch01/evdlg/evt_count_3
lnhud waypoint @a clear
execute unless score #rc ln matches 2 run lnhud waypoint @a 101 126 1462
execute unless score #rb ln matches 2 run lnhud waypoint @a 22 127 1324
execute unless score #ra ln matches 2 run lnhud waypoint @a 28 129 1290
