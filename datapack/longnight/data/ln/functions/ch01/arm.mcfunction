# 由 tools/build_ch01.py 自動產生，請勿手動修改
kill @e[tag=c1_c4a]
kill @e[tag=c1_c4b]
kill @e[tag=c1_c4c]
kill @e[tag=c1_lbla]
kill @e[tag=c1_lblb]
kill @e[tag=c1_lblc]
execute unless score #ra ln matches 2 run summon interaction 28.5 129 1290.5 {Tags:["ln","c1_c4a"],width:1.6f,height:1.8f,response:1b}
execute unless score #ra ln matches 2 run summon text_display 28.5 131.4 1290.5 {Tags:["ln","c1_lbla"],billboard:"center",see_through:1b,transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[2.5f,2.5f,2.5f]},brightness:{sky:15,block:15},background:1711276032,text:'{"text": "北崖雷達：安裝 C4（右鍵）", "color": "#F0A040", "font": "lnai:ui"}'}
execute unless score #ra ln matches 2 run scoreboard players set #ra ln 0
execute unless score #rb ln matches 2 run summon interaction 22.5 127 1324.5 {Tags:["ln","c1_c4b"],width:1.6f,height:1.8f,response:1b}
execute unless score #rb ln matches 2 run summon text_display 22.5 129.4 1324.5 {Tags:["ln","c1_lblb"],billboard:"center",see_through:1b,transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[2.5f,2.5f,2.5f]},brightness:{sky:15,block:15},background:1711276032,text:'{"text": "中央雷達：安裝 C4（右鍵）", "color": "#F0A040", "font": "lnai:ui"}'}
execute unless score #rb ln matches 2 run scoreboard players set #rb ln 0
execute unless score #rc ln matches 2 run summon interaction 101.5 126 1462.5 {Tags:["ln","c1_c4c"],width:1.6f,height:1.8f,response:1b}
execute unless score #rc ln matches 2 run summon text_display 101.5 128.4 1462.5 {Tags:["ln","c1_lblc"],billboard:"center",see_through:1b,transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[2.5f,2.5f,2.5f]},brightness:{sky:15,block:15},background:1711276032,text:'{"text": "燈塔雷達：安裝 C4（右鍵）", "color": "#F0A040", "font": "lnai:ui"}'}
execute unless score #rc ln matches 2 run scoreboard players set #rc ln 0
