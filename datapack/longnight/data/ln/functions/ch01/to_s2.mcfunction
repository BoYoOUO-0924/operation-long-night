# 由 tools/build_ch01.py 自動產生，請勿手動修改
scoreboard players set #stage ln 2
scoreboard players set #t ln 0
scoreboard players set #c1lt ln 0
kill @e[tag=c1_beam1]
kill @e[tag=c1_beacon]
kill @e[tag=c1_chute_e]
effect clear @e[tag=ln_ally] slow_falling
function ln:ch01/evdlg/landed
scoreboard players set #light ln 0
scoreboard players set #aa ln 0
scoreboard players set #cable ln 0
scoreboard players set #bar ln 0
scoreboard players set #scan ln 0
scoreboard players set #aaf ln 0
execute store result score #players ln if entity @a[gamemode=adventure]
summon pig 68.5 89 1406.5 {Tags:["ln","c1_cable"],NoAI:1b,NoGravity:1b,Silent:1b,PersistenceRequired:1b,Invulnerable:0b,DeathLootTable:"minecraft:empty",Health:1000f,Attributes:[{Name:"generic.max_health",Base:1000d}],ActiveEffects:[{Id:14,Duration:-1,Amplifier:0b,ShowParticles:0b}]}
summon pig 53.5 91 1431.5 {Tags:["ln","c1_barrels"],NoAI:1b,NoGravity:1b,Silent:1b,PersistenceRequired:1b,Invulnerable:0b,DeathLootTable:"minecraft:empty",Health:1000f,Attributes:[{Name:"generic.max_health",Base:1000d}],ActiveEffects:[{Id:14,Duration:-1,Amplifier:0b,ShowParticles:0b}]}
summon interaction 56.5 93 1428.5 {Tags:["ln","c1_aa_btn"],width:1.6f,height:1.6f,response:1b}
summon text_display 56.5 95.2 1428.5 {Tags:["ln","c1_aa_lbl"],billboard:"center",see_through:1b,transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[2.5f,2.5f,2.5f]},brightness:{sky:15,block:15},background:1711276032,text:'{"text": "安裝 C4（右鍵）", "color": "#F0A040", "font": "lnai:ui"}'}
scoreboard players set #callout ln 0
function ln:ch01/sq/shelf_south
execute as @e[tag=ln_fresh] run data merge entity @s {ForgeData:{ln_wp:[I;60,89,1420],ln_wpr:4,ln_hunt:22}}
tag @e[tag=ln_fresh] remove ln_fresh
scoreboard players set #callout ln 0
function ln:ch01/sq/gate_inside
execute as @e[tag=ln_fresh] run data merge entity @s {ForgeData:{ln_wp:[I;66,88,1406],ln_wpr:4,ln_hunt:22}}
tag @e[tag=ln_fresh] remove ln_fresh
lnhud waypoint @a 82 64 1400
bossbar set ln:obj name {"text": "目標：破壞探照燈和防空砲", "font": "lnai:ui"}
bossbar set ln:obj color yellow
lnhud music @a ch05_suspense 60
