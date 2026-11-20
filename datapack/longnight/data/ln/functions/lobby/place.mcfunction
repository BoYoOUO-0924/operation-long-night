# 由 tools/build_lobby.py 自動產生，請勿手動修改
forceload add -334 898 -270 956
fillbiome -334 270 898 -270 294 905 minecraft:the_void
fillbiome -334 270 906 -270 294 913 minecraft:the_void
fillbiome -334 270 914 -270 294 921 minecraft:the_void
fillbiome -334 270 922 -270 294 929 minecraft:the_void
fillbiome -334 270 930 -270 294 937 minecraft:the_void
fillbiome -334 270 938 -270 294 945 minecraft:the_void
fillbiome -334 270 946 -270 294 953 minecraft:the_void
fillbiome -334 270 954 -270 294 956 minecraft:the_void
execute positioned -310 272 900 run function ln:build/transport_plane
kill @e[tag=ln_lobby]
summon tacznpcs:npc -303.5 273.75 904.5 {template:"blue_support",templateInitialized:1b,skin:{texture:"tacznpcs:entity/villager1.png",slim:0b},NoAI:1b,NoGravity:1b,Invulnerable:1b,Silent:1b,PersistenceRequired:1b,Rotation:[180f,0f],Tags:["ln_lobby","lb_pilot"],HandItems:[{},{}],ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:3355443}}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:4934475}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:5592405}}},{id:"zerocontact:helmet_airframe",Count:1b}]}
summon tacznpcs:npc -299.5 273.75 904.5 {template:"blue_support",templateInitialized:1b,skin:{texture:"tacznpcs:entity/villager1.png",slim:0b},NoAI:1b,NoGravity:1b,Invulnerable:1b,Silent:1b,PersistenceRequired:1b,Rotation:[180f,0f],Tags:["ln_lobby","lb_pilot"],HandItems:[{},{}],ArmorItems:[{id:"minecraft:leather_boots",Count:1b,tag:{display:{color:3355443}}},{id:"minecraft:leather_leggings",Count:1b,tag:{display:{color:4934475}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:5592405}}},{id:"zerocontact:helmet_airframe",Count:1b}]}
summon tacznpcs:npc -296.5 273.75 929.5 {template:"blue_support",CustomName:'{"text": "戰車", "color": "gold"}',NoAI:1b,NoGravity:1b,Invulnerable:1b,PersistenceRequired:1b,Rotation:[90f,0f],Tags:["ln_lobby","lb_squad","lb_tank"]}
summon tacznpcs:npc -295.5 273 931.5 {template:"blue_sniper",CustomName:'{"text": "白鴉", "color": "aqua"}',NoAI:1b,NoGravity:1b,Invulnerable:1b,PersistenceRequired:1b,Rotation:[90f,0f],Tags:["ln_lobby","lb_squad","lb_baiya"]}
summon tacznpcs:npc -296.5 273 933.5 {template:"blue_assault",CustomName:'{"text": "狐狸", "color": "green"}',NoAI:1b,NoGravity:1b,Invulnerable:1b,PersistenceRequired:1b,Rotation:[-90f,0f],Tags:["ln_lobby","lb_squad","lb_fox"]}
schedule function ln:lobby/dress 3t replace
summon text_display -301.5 275.95 911.5 {Tags:["ln_lobby","lb_title"],billboard:"vertical",background:0,transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.8f,0.8f,0.8f]},text:'{"text": "作戰簡報  MISSION BRIEFING", "color": "#7FC8E8", "font": "lnai:ui"}'}
summon text_display -301.5 275.0 911.5 {Tags:["ln_lobby","lb_chap"],billboard:"vertical",background:1711276032,transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[1.1f,1.1f,1.1f]},text:'""'}
summon text_display -301.5 274.55 911.5 {Tags:["ln_lobby","lb_status"],billboard:"vertical",background:0,text:'""'}
summon interaction -303.5 274 912.45 {Tags:["ln_lobby","lb_prev"],width:0.8f,height:0.6f,response:1b}
summon text_display -303.5 274.15 912.45 {Tags:["ln_lobby","lb_prev_t"],billboard:"vertical",background:1711276032,transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[1.2f,1.2f,1.2f]},text:'{"text": "◀", "color": "#E4E2DA", "font": "lnai:ui"}'}
summon interaction -301.5 274 912.45 {Tags:["ln_lobby","lb_ready"],width:1.6f,height:0.6f,response:1b}
summon text_display -301.5 274.15 912.45 {Tags:["ln_lobby","lb_ready_t"],billboard:"vertical",background:1711276032,transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[1.2f,1.2f,1.2f]},text:'{"text": "[ 準備就緒 ]", "color": "#8EE07A", "font": "lnai:ui"}'}
summon interaction -298.5 274 912.45 {Tags:["ln_lobby","lb_next"],width:0.8f,height:0.6f,response:1b}
summon text_display -298.5 274.15 912.45 {Tags:["ln_lobby","lb_next_t"],billboard:"vertical",background:1711276032,transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[1.2f,1.2f,1.2f]},text:'{"text": "▶", "color": "#E4E2DA", "font": "lnai:ui"}'}
summon block_display -303.00 274 911.16 {Tags:["ln_lobby"],brightness:{sky:15,block:15},block_state:{Name:"minecraft:white_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.32f,0.21f,0.32f]}}
summon block_display -301.37 274 910.49 {Tags:["ln_lobby"],brightness:{sky:15,block:15},block_state:{Name:"minecraft:white_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.32f,0.08f,0.32f]}}
summon block_display -302.91 274 910.73 {Tags:["ln_lobby"],brightness:{sky:15,block:15},block_state:{Name:"minecraft:white_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.32f,0.43f,0.32f]}}
summon block_display -301.73 274 911.17 {Tags:["ln_lobby"],brightness:{sky:15,block:15},block_state:{Name:"minecraft:cyan_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.32f,0.22f,0.32f]}}
summon block_display -303.03 274 910.61 {Tags:["ln_lobby"],brightness:{sky:15,block:15},block_state:{Name:"minecraft:white_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.32f,0.40f,0.32f]}}
summon block_display -300.89 274 911.34 {Tags:["ln_lobby"],brightness:{sky:15,block:15},block_state:{Name:"minecraft:light_blue_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.32f,0.10f,0.32f]}}
summon block_display -302.73 274 910.44 {Tags:["ln_lobby"],brightness:{sky:15,block:15},block_state:{Name:"minecraft:white_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.32f,0.38f,0.32f]}}
summon block_display -301.50 274 911.69 {Tags:["ln_lobby"],brightness:{sky:15,block:15},block_state:{Name:"minecraft:white_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.32f,0.22f,0.32f]}}
summon block_display -302.34 274 911.52 {Tags:["ln_lobby"],brightness:{sky:15,block:15},block_state:{Name:"minecraft:cyan_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.32f,0.24f,0.32f]}}
summon block_display -300.31 274 910.54 {Tags:["ln_lobby"],brightness:{sky:15,block:15},block_state:{Name:"minecraft:cyan_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.32f,0.13f,0.32f]}}
summon block_display -302.92 274 911.34 {Tags:["ln_lobby"],brightness:{sky:15,block:15},block_state:{Name:"minecraft:light_blue_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.32f,0.35f,0.32f]}}
summon block_display -302.23 274 911.57 {Tags:["ln_lobby"],brightness:{sky:15,block:15},block_state:{Name:"minecraft:white_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.32f,0.28f,0.32f]}}
summon block_display -301.55 274 911.67 {Tags:["ln_lobby"],brightness:{sky:15,block:15},block_state:{Name:"minecraft:light_blue_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.32f,0.32f,0.32f]}}
summon block_display -300.40 274 911.79 {Tags:["ln_lobby"],brightness:{sky:15,block:15},block_state:{Name:"minecraft:cyan_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.32f,0.31f,0.32f]}}
summon block_display -301.07 274 910.86 {Tags:["ln_lobby"],brightness:{sky:15,block:15},block_state:{Name:"minecraft:light_blue_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.32f,0.27f,0.32f]}}
summon block_display -301.00 274 910.70 {Tags:["ln_lobby"],brightness:{sky:15,block:15},block_state:{Name:"minecraft:light_blue_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.32f,0.37f,0.32f]}}
summon block_display -302.80 274 910.49 {Tags:["ln_lobby"],brightness:{sky:15,block:15},block_state:{Name:"minecraft:white_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.32f,0.38f,0.32f]}}
summon block_display -303.63 274 911.52 {Tags:["ln_lobby"],brightness:{sky:15,block:15},block_state:{Name:"minecraft:cyan_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.32f,0.22f,0.32f]}}
summon block_display -303.92 274 911.00 {Tags:["ln_lobby"],brightness:{sky:15,block:15},block_state:{Name:"minecraft:light_blue_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.32f,0.23f,0.32f]}}
summon block_display -303.81 274 911.26 {Tags:["ln_lobby"],brightness:{sky:15,block:15},block_state:{Name:"minecraft:light_blue_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.32f,0.10f,0.32f]}}
summon block_display -301.69 274 911.69 {Tags:["ln_lobby"],brightness:{sky:15,block:15},block_state:{Name:"minecraft:cyan_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.32f,0.18f,0.32f]}}
summon block_display -299.81 274 910.83 {Tags:["ln_lobby"],brightness:{sky:15,block:15},block_state:{Name:"minecraft:light_blue_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.32f,0.11f,0.32f]}}
summon block_display -300.01 274 911.76 {Tags:["ln_lobby"],brightness:{sky:15,block:15},block_state:{Name:"minecraft:light_blue_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.32f,0.18f,0.32f]}}
summon block_display -303.34 274 910.46 {Tags:["ln_lobby"],brightness:{sky:15,block:15},block_state:{Name:"minecraft:light_blue_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.32f,0.38f,0.32f]}}
summon block_display -302.49 274 910.59 {Tags:["ln_lobby"],brightness:{sky:15,block:15},block_state:{Name:"minecraft:white_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.32f,0.38f,0.32f]}}
summon block_display -302.07 274 911.13 {Tags:["ln_lobby"],brightness:{sky:15,block:15},block_state:{Name:"minecraft:light_blue_stained_glass"},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.32f,0.31f,0.32f]}}
scoreboard players set #placed ln 1
scoreboard players set #c20 ln 20
execute unless score #chap ln matches 1..8 run scoreboard players set #chap ln 5
function ln:lobby/show_chap
function ln:lobby/reset_jump
