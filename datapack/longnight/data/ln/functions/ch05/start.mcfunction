# 由 tools/build_level.py 自動產生，請勿手動修改
function ln:ch05/cleanup
forceload add 50 900 240 1020
function ln:build/station_place
kill @e[type=item]
time set 18000
weather thunder 1000000
scoreboard players set #wave ln 0
gamemode adventure @a
clear @a
spreadplayers 178 958 0 3 false @a
execute as @a at @s run spawnpoint @s ~ ~ ~
function ln:ch05/loadout
function ln:ch05/spawn_allies_start
bossbar set ln:obj players @a
bossbar set ln:obj visible true
bossbar set ln:obj max 1
bossbar set ln:obj value 1
bossbar set ln:obj name {"text": "目標：前往山上的氣象站"}
bossbar set ln:obj color yellow
title @a times 20 80 20
title @a subtitle {"text": "零下四十度", "color": "gray"}
title @a title {"text": "第五章　寒霜陷阱", "color": "white", "bold": true}
scoreboard players set #stage ln 1
scoreboard players set #t ln 0
