# 由 tools/build_ch01.py 自動產生，請勿手動修改
scoreboard players set #rb ln 2
kill @e[tag=c1_c4b]
kill @e[tag=c1_c4vis_b]
kill @e[tag=c1_lblb]
particle minecraft:explosion_emitter 24 131 1322 1 1 1 0 2 force @a
particle minecraft:large_smoke 24 131 1322 1.5 1.5 1.5 0.05 40 force @a
particle minecraft:lava 24 131 1322 1 1 1 0 20 force @a
playsound lnai:sfx.boom master @a 24 131 1322 6 0.9
playsound minecraft:entity.generic.explode master @a 24 131 1322 4 0.7
particle minecraft:explosion 24 138 1322 1 1 1 0 6 force @a
particle minecraft:large_smoke 24 138 1322 1.5 1.5 1.5 0.05 40 force @a
particle minecraft:lava 24 138 1322 1 1 1 0 20 force @a
playsound lnai:sfx.boom master @a 24 138 1322 6 0.9
playsound minecraft:entity.generic.explode master @a 24 138 1322 4 0.7
fill 20 127 1317 29 141 1327 air
fill 11 127 1320 17 132 1326 air
particle minecraft:explosion 14 129 1323 1 1 1 0 6 force @a
particle minecraft:large_smoke 14 129 1323 1.5 1.5 1.5 0.05 40 force @a
particle minecraft:lava 14 129 1323 1 1 1 0 20 force @a
playsound lnai:sfx.boom master @a 14 129 1323 6 0.9
playsound minecraft:entity.generic.explode master @a 14 129 1323 4 0.7
fill 21 127 1319 27 127 1320 smooth_quartz_slab
setblock 22 127 1325 iron_bars
setblock 23 127 1324 campfire[lit=true]
setblock 24 127 1322 campfire[lit=true]
execute positioned 24 127 1322 run kill @e[tag=ln_enemy,distance=..6]
lnhud tint @a 50FFE0B0 10 pulse
scoreboard players add #count ln 1
function ln:ch01/evdlg/evt_boom_b
execute if score #count ln matches 1 run function ln:ch01/evdlg/evt_count_1
execute if score #count ln matches 2 run function ln:ch01/evdlg/evt_count_2
execute if score #count ln matches 3 run function ln:ch01/evdlg/evt_count_3
lnhud waypoint @a clear
execute unless score #rc ln matches 2 run lnhud waypoint @a 101 126 1462
execute unless score #rb ln matches 2 run lnhud waypoint @a 22 127 1324
execute unless score #ra ln matches 2 run lnhud waypoint @a 28 129 1290
