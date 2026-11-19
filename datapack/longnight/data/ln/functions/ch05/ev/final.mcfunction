# 由 tools/build_level.py 自動產生，請勿手動修改
scoreboard players set #final ln 1
function ln:ch05/evdlg/final_assault
scoreboard players set #route ln 0
function ln:ch05/dir/spawn_next
scoreboard players set #route ln 1
function ln:ch05/dir/spawn_next
summon superbwarfare:sodayo_pick_up_hmg 164 128 962 {Rotation:[90f,0f],Tags:["ln","ln_tech"]}
summon tacznpcs:npc 164 130 962 {template:"red_support",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_techgun"],ForgeData:{ln_side:"red",ln_hunt:64}}
summon tacznpcs:npc 164 130 962 {template:"red_assault",PersistenceRequired:1b,Tags:["ln","ln_enemy","ln_techgun"],ForgeData:{ln_side:"red",ln_hunt:64}}
execute as @e[tag=ln_techgun] run ride @s mount @e[tag=ln_tech,limit=1]
team join ln_red @e[tag=ln_techgun]
scoreboard players set #tp ln 1
scoreboard players set #tpt ln 0
scoreboard players set #mort ln 6
scoreboard players set #mt ln 0
