# 由 tools/build_level.py 自動產生，請勿手動修改
summon tacznpcs:npc 178 250 958 {template:"blue_sniper",CustomName:'{"text": "白鴉", "color": "aqua"}',CustomNameVisible:1b,Invulnerable:1b,PersistenceRequired:1b,Tags:["ln","ln_ally","ln_baiya","ln_new"]}
summon tacznpcs:npc 178 250 958 {template:"blue_support",CustomName:'{"text": "戰車", "color": "gold"}',CustomNameVisible:1b,Invulnerable:1b,PersistenceRequired:1b,Tags:["ln","ln_ally","ln_tank","ln_new"]}
summon tacznpcs:npc 178 250 958 {template:"blue_assault",CustomName:'{"text": "狐狸", "color": "green"}',CustomNameVisible:1b,Invulnerable:1b,PersistenceRequired:1b,Tags:["ln","ln_ally","ln_fox","ln_new"]}
summon tacznpcs:npc 178 250 958 {template:"ln_officer",CustomName:'{"text": "情報官", "color": "gray"}',CustomNameVisible:1b,Invulnerable:1b,PersistenceRequired:1b,NoAI:1b,Tags:["ln","ln_ally","ln_officer","ln_new"]}
spreadplayers 178 958 2 5 false @e[tag=ln_new]
tag @e[tag=ln_new] remove ln_new
