# 由 tools/build_level.py 自動產生，請勿手動修改
scoreboard players set #stage ln 4
scoreboard players set #t ln 0
function ln:ch05/ammo
give @a[gamemode=adventure] golden_apple 2
bossbar set ln:obj name {"text": "準備防守：敵軍即將抵達"}
bossbar set ln:obj color red
bossbar set ln:obj max 400
execute as @e[tag=ln_tank] run data merge entity @s {ForgeData:{ln_follow:1b,ln_hunt:40}}
execute as @e[tag=ln_fox] run data merge entity @s {ForgeData:{ln_follow:1b,ln_hunt:40}}
tellraw @a [{"text": "[戰車] ", "color": "gold", "bold": true}, {"text": "我和狐狸跟著你，你往哪打我們就往哪打。白鴉在塔上掩護。", "color": "white"}]
data merge entity @e[tag=ln_baiya,limit=1] {ForgeData:{ln_wp:[I;88,142,959],ln_wpr:1,ln_hunt:64}}
