# 由 tools/build_ch01.py 自動產生，請勿手動修改
scoreboard players set #aa ln 1
scoreboard players set #aaf ln 0
kill @e[tag=c1_barrels]
kill @e[tag=c1_aa_btn]
kill @e[tag=c1_aa_lbl]
particle minecraft:explosion_emitter 56 93 1428 1 1 1 0 2 force @a
particle minecraft:large_smoke 56 93 1428 1.5 1.5 1.5 0.05 40 force @a
particle minecraft:lava 56 93 1428 1 1 1 0 20 force @a
playsound lnai:sfx.boom master @a 56 93 1428 6 0.9
playsound minecraft:entity.generic.explode master @a 56 93 1428 4 0.7
fill 55 92 1426 61 98 1430 air replace end_rod
setblock 56 92 1428 campfire[lit=true]
setblock 56 93 1428 air
fill 53 91 1430 54 92 1431 black_concrete replace red_concrete
execute positioned 56 93 1428 run kill @e[tag=ln_enemy,distance=..5]
function ln:ch01/evdlg/evt_aa_down
execute if score #light ln matches 0 run lnhud waypoint @a 73 96 1406
