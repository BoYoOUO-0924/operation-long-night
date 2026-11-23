# 由 tools/build_ch01.py 自動產生，請勿手動修改
function ln:ch05/cleanup
function ln:ch01/cleanup
forceload add -16 1250 140 1480
execute positioned 0 0 0 run function ln:build/coast_battery
kill @e[type=item]
time set 18000
weather rain 1000000
scoreboard objectives add ln_lit dummy
scoreboard objectives add ln_pid dummy
scoreboard players set @a ln_lit 0
scoreboard players reset @a ln_pid
scoreboard players set #k ln 0
gamemode adventure @a
gamerule naturalRegeneration false
effect give @a instant_health 1 9 true
team join ln_blue @a
clear @a
function ln:ch01/loadout
tag @a[gamemode=adventure] add c1_nopid
execute as @a[tag=c1_nopid,limit=1,sort=random] run function ln:ch01/pid_1
execute as @a[tag=c1_nopid,limit=1,sort=random] run function ln:ch01/pid_2
execute as @a[tag=c1_nopid,limit=1,sort=random] run function ln:ch01/pid_3
execute as @a[tag=c1_nopid,limit=1,sort=random] run function ln:ch01/pid_4
tag @a remove c1_nopid
setblock 122 299 1406 barrier
setblock 126 299 1414 barrier
setblock 122 299 1422 barrier
setblock 128 299 1428 barrier
tp @a[scores={ln_pid=1}] 122.5 300 1406.5 90 20
tp @a[scores={ln_pid=2}] 126.5 300 1414.5 90 20
tp @a[scores={ln_pid=3}] 122.5 300 1422.5 90 20
tp @a[scores={ln_pid=4}] 128.5 300 1428.5 90 20
function ln:ch01/fleet
spawnpoint @a 92 64 1414
summon block_display 74.5 96.5 1406.5 {Tags:["ln","c1_beam0"],brightness:{sky:15,block:15},view_range:4f,block_state:{Name:"minecraft:white_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[-0.450f,-0.450f,0f],scale:[0.9f,0.9f,14f]}}
summon block_display 74.5 96.5 1406.5 {Tags:["ln","c1_beam0"],brightness:{sky:12,block:12},view_range:4f,block_state:{Name:"minecraft:white_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[-0.375f,-0.375f,14f],scale:[0.75f,0.75f,16f]}}
summon block_display 74.5 96.5 1406.5 {Tags:["ln","c1_beam0"],brightness:{sky:9,block:9},view_range:4f,block_state:{Name:"minecraft:light_gray_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[-0.300f,-0.300f,30f],scale:[0.6f,0.6f,16f]}}
summon block_display 74.5 96.5 1406.5 {Tags:["ln","c1_beam0"],brightness:{sky:6,block:6},view_range:4f,block_state:{Name:"minecraft:light_gray_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[-0.225f,-0.225f,46f],scale:[0.45f,0.45f,14f]}}
summon block_display 74.5 96.5 1406.5 {Tags:["ln","c1_beam0"],brightness:{sky:4,block:4},view_range:4f,block_state:{Name:"minecraft:gray_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[-0.150f,-0.150f,60f],scale:[0.3f,0.3f,10f]}}
summon block_display 100.5 127.5 1462.5 {Tags:["ln","c1_beam1"],brightness:{sky:15,block:15},view_range:4f,block_state:{Name:"minecraft:white_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[-0.450f,-0.450f,0f],scale:[0.9f,0.9f,14f]}}
summon block_display 100.5 127.5 1462.5 {Tags:["ln","c1_beam1"],brightness:{sky:12,block:12},view_range:4f,block_state:{Name:"minecraft:white_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[-0.375f,-0.375f,14f],scale:[0.75f,0.75f,16f]}}
summon block_display 100.5 127.5 1462.5 {Tags:["ln","c1_beam1"],brightness:{sky:9,block:9},view_range:4f,block_state:{Name:"minecraft:light_gray_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[-0.300f,-0.300f,30f],scale:[0.6f,0.6f,16f]}}
summon block_display 100.5 127.5 1462.5 {Tags:["ln","c1_beam1"],brightness:{sky:6,block:6},view_range:4f,block_state:{Name:"minecraft:light_gray_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[-0.225f,-0.225f,46f],scale:[0.45f,0.45f,14f]}}
summon block_display 100.5 127.5 1462.5 {Tags:["ln","c1_beam1"],brightness:{sky:4,block:4},view_range:4f,block_state:{Name:"minecraft:gray_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[-0.150f,-0.150f,60f],scale:[0.3f,0.3f,10f]}}
function ln:ch01/spawn_allies
bossbar set ln:obj players @a
bossbar set ln:obj visible true
bossbar set ln:obj max 1
bossbar set ln:obj value 1
bossbar set ln:obj name {"text": "目標：降落到沙灘", "font": "lnai:ui"}
bossbar set ln:obj color yellow
lnhud waypoint @a 92 64 1414
summon marker 92 64 1414 {Tags:["ln","c1_beacon"]}
scoreboard players set #litsaid ln 0
scoreboard players set #landed ln 0
scoreboard players set #c1lt ln 0
scoreboard players set #sk ln 0
scoreboard players set #run ln 1
scoreboard players reset #count ln
scoreboard players reset #tl ln
scoreboard players set #fail ln 0
scoreboard players set #endt ln 0
scoreboard players reset #near_b ln
scoreboard players reset #near_c ln
scoreboard players reset #ra ln
scoreboard players reset #rb ln
scoreboard players reset #rc ln
scoreboard players set #stage ln 9
scoreboard players set #t ln 0
lnhud tint @a 00000000 30
lnhud cutscene @a ln:ch01_intro
lnhud ambient @a stop 20
