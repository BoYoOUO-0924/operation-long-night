# 由 tools/build_ch01.py 自動產生，請勿手動修改
scoreboard players set #light ln 1
kill @e[tag=c1_beam0]
kill @e[tag=c1_cable]
kill @e[tag=c1_cable_lbl]
setblock 73 96 1406 redstone_lamp[lit=false]
setblock 74 96 1406 gray_concrete
particle minecraft:electric_spark 68 89 1406 0.5 0.5 0.5 0.3 60 force @a
playsound minecraft:block.beacon.deactivate master @a 73 96 1406 3 0.6
function ln:ch01/evdlg/evt_light_out
execute if score #aa ln matches 0 run lnhud waypoint @a 56 93 1428
