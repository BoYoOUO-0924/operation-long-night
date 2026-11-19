# 由 tools/build_level.py 自動產生，請勿手動修改
scoreboard players set #stage ln 4
scoreboard players set #t ln 0
function ln:ch05/ammo
bossbar set ln:obj name {"text": "準備防守：敵軍即將抵達"}
bossbar set ln:obj color red
bossbar set ln:obj max 400
data merge entity @e[tag=ln_tank,limit=1] {ForgeData:{ln_wp:[I;124,136,965],ln_wpr:2,ln_hunt:40}}
data merge entity @e[tag=ln_fox,limit=1] {ForgeData:{ln_wp:[I;87,136,965],ln_wpr:2,ln_hunt:40}}
data merge entity @e[tag=ln_baiya,limit=1] {ForgeData:{ln_wp:[I;88,142,959],ln_wpr:1,ln_hunt:64}}
