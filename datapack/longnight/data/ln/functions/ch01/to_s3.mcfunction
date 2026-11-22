# 由 tools/build_ch01.py 自動產生，請勿手動修改
scoreboard players set #stage ln 3
scoreboard players set #t ln 0
function ln:ch01/evdlg/evt_hack
tp @e[tag=ln_fox] 49 110 1374
execute as @e[tag=ln_fox] run data merge entity @s {ForgeData:{ln_follow:0b}}
lnhud waypoint @a 49 111 1373
bossbar set ln:obj max 200
bossbar set ln:obj value 0
bossbar set ln:obj name {"text": "狐狸正在破解大門電子鎖……", "font": "lnai:ui"}
bossbar set ln:obj color blue
scoreboard players set #callout ln 1
function ln:ch01/sq/shelf_south
execute as @e[tag=ln_fresh] run data merge entity @s {ForgeData:{ln_wp:[I;49,110,1379],ln_wpr:4,ln_hunt:40}}
tag @e[tag=ln_fresh] remove ln_fresh
