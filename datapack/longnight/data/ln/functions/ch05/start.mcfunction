# 由 tools/build_level.py 自動產生，請勿手動修改
function ln:ch05/cleanup
forceload add 50 900 240 1020
function ln:build/station_place
function ln:build/wreck_place
kill @e[type=item]
time set 18000
weather thunder 1000000
scoreboard players set #c2 ln 2
scoreboard players set #c3 ln 3
scoreboard players set #c8 ln 8
scoreboard players set #c100 ln 100
gamemode adventure @a
gamerule naturalRegeneration false
team join ln_blue @a
clear @a
spreadplayers 178 958 0 3 false @a
execute as @a at @s run spawnpoint @s ~ ~ ~
function ln:ch05/loadout
function ln:ch05/spawn_allies_start
bossbar set ln:obj players @a
bossbar set ln:obj visible true
bossbar set ln:obj max 1
bossbar set ln:obj value 1
bossbar set ln:obj name {"text": "目標：前往山上的氣象站", "font": "lnai:ui"}
bossbar set ln:obj color yellow
scoreboard players set #stage ln 0
scoreboard players set #t ln 0
lnhud music @a ch05_ice 20
lnhud ambient @a blizzard_loop 40
lnhud cutscene @a ln:ch05_intro
