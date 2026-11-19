# 由 tools/build_level.py 自動產生，請勿手動修改
summon tacznpcs:npc 178 250 958 {template:"blue_sniper",CustomName:'{"text": "白鴉", "color": "aqua"}',CustomNameVisible:1b,Invulnerable:1b,PersistenceRequired:1b,Tags:["ln","ln_ally","ln_baiya","ln_new"],ForgeData:{ln_side:"blue",ln_follow:1b,ln_slot:1,ln_hunt:24}}
summon tacznpcs:npc 178 250 958 {template:"blue_support",CustomName:'{"text": "戰車", "color": "gold"}',CustomNameVisible:1b,Invulnerable:1b,PersistenceRequired:1b,Tags:["ln","ln_ally","ln_tank","ln_new"],ForgeData:{ln_side:"blue",ln_follow:1b,ln_slot:2,ln_hunt:24}}
summon tacznpcs:npc 178 250 958 {template:"blue_assault",CustomName:'{"text": "狐狸", "color": "green"}',CustomNameVisible:1b,Invulnerable:1b,PersistenceRequired:1b,Tags:["ln","ln_ally","ln_fox","ln_new"],ForgeData:{ln_side:"blue",ln_follow:1b,ln_slot:3,ln_hunt:24}}
summon tacznpcs:npc 178 250 958 {template:"ln_officer",CustomName:'{"text": "情報官", "color": "gray"}',CustomNameVisible:1b,Invulnerable:1b,PersistenceRequired:1b,Tags:["ln","ln_ally","ln_officer","ln_new"],ForgeData:{ln_side:"blue",ln_follow:1b,ln_slot:4}}
spreadplayers 178 958 2 5 false @e[tag=ln_new]
team join ln_blue @e[tag=ln_new]
effect give @e[tag=ln_new,tag=!ln_officer] glowing infinite 0 true
tag @e[tag=ln_new] remove ln_new
