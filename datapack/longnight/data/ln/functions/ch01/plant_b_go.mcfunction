# 由 tools/build_ch01.py 自動產生，請勿手動修改
scoreboard players set #rb ln 1
scoreboard players set #fb ln 300
kill @e[tag=c1_lblb]
playsound minecraft:block.note_block.bit master @a 22 127 1324 2 1.6
function ln:ch01/evdlg/evt_plant_b
scoreboard players set #callout ln 1
function ln:ch01/sq/plateau_west
execute as @e[tag=ln_fresh] run data merge entity @s {ForgeData:{ln_wp:[I;22,127,1324],ln_wpr:4,ln_hunt:48}}
tag @e[tag=ln_fresh] remove ln_fresh
summon block_display 22.3 128 1324.3 {Tags:["ln","c1_c4vis_b"],block_state:{Name:"minecraft:tnt"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.4f,0.3f,0.4f]},brightness:{sky:15,block:15}}
