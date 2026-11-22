# 由 tools/build_ch01.py 自動產生，請勿手動修改
scoreboard players set #ra ln 1
scoreboard players set #fa ln 300
kill @e[tag=c1_lbla]
playsound minecraft:block.note_block.bit master @a 28 129 1290 2 1.6
function ln:ch01/evdlg/evt_plant_a
scoreboard players set #callout ln 1
function ln:ch01/sq/plateau_north
execute as @e[tag=ln_fresh] run data merge entity @s {ForgeData:{ln_wp:[I;28,129,1290],ln_wpr:4,ln_hunt:48}}
tag @e[tag=ln_fresh] remove ln_fresh
summon block_display 28.3 130 1290.3 {Tags:["ln","c1_c4vis_a"],block_state:{Name:"minecraft:tnt"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.4f,0.3f,0.4f]},brightness:{sky:15,block:15}}
