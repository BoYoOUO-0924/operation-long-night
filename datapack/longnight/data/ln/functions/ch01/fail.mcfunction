# 由 tools/build_ch01.py 自動產生，請勿手動修改
scoreboard players add #fail ln 1
function ln:ch01/evdlg/evt_fail
kill @e[tag=ln_enemy]
scoreboard players set #tl ln 6000
execute if score #ra ln matches 1 run kill @e[tag=c1_c4vis_a]
execute if score #rb ln matches 1 run kill @e[tag=c1_c4vis_b]
execute if score #rc ln matches 1 run kill @e[tag=c1_c4vis_c]
function ln:ch01/arm
scoreboard players set #dt ln 0
