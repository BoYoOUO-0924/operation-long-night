# 由 tools/build_level.py 自動產生，請勿手動修改
scoreboard players set #tp ln 0
execute as @e[tag=ln_techgun] run ride @s dismount
execute as @e[tag=ln_techgun] run data merge entity @s {ForgeData:{ln_wp:[I;132,136,961],ln_wpr:3,ln_hunt:64}}
tellraw @a [{"text": "[白鴉] ", "color": "aqua", "bold": true}, {"text": "皮卡停了，槍手下車了！東邊車庫外！", "color": "white"}]
