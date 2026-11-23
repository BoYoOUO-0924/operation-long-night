# 由 tools/build_ch01.py 自動產生，請勿手動修改
summon tacznpcs:npc 131 299.5 1413 {template:"blue_sniper",CustomName:'{"text": "白鴉", "color": "aqua", "font": "lnai:ui"}',CustomNameVisible:1b,Invulnerable:1b,PersistenceRequired:1b,Tags:["ln","ln_ally","ln_baiya","ln_new","ln_dress"],ForgeData:{ln_side:"blue",ln_follow:1b,ln_slot:1,ln_hunt:24}}
summon tacznpcs:npc 135 301 1417 {template:"blue_support",CustomName:'{"text": "戰車", "color": "gold", "font": "lnai:ui"}',CustomNameVisible:1b,Invulnerable:1b,PersistenceRequired:1b,Tags:["ln","ln_ally","ln_tank","ln_new","ln_dress"],ForgeData:{ln_side:"blue",ln_follow:1b,ln_slot:2,ln_hunt:24}}
summon tacznpcs:npc 132 298 1421 {template:"blue_assault",CustomName:'{"text": "狐狸", "color": "green", "font": "lnai:ui"}',CustomNameVisible:1b,Invulnerable:1b,PersistenceRequired:1b,Tags:["ln","ln_ally","ln_fox","ln_new","ln_dress"],ForgeData:{ln_side:"blue",ln_follow:1b,ln_slot:3,ln_hunt:24}}
team join ln_blue @e[tag=ln_new]
effect give @e[tag=ln_new] glowing infinite 0 true
effect give @e[tag=ln_new] slow_falling 120 0 true
tag @e[tag=ln_new] remove ln_new
schedule function ln:ch05/dress 2t replace
