# 由 tools/build_level.py 自動產生，請勿手動修改
execute as @e[tag=ln_enemy,tag=rt_east,scores={ln_age=2}] run data merge entity @s {ForgeData:{ln_wp:[I;150,133,962],ln_wpr:3,ln_hunt:20}}
execute as @e[tag=ln_enemy,tag=rt_east,scores={ln_age=220}] run data merge entity @s {ForgeData:{ln_wp:[I;132,136,961],ln_wpr:3,ln_hunt:40}}
execute as @e[tag=ln_enemy,tag=rt_north,scores={ln_age=2}] run data merge entity @s {ForgeData:{ln_wp:[I;100,131,940],ln_wpr:3,ln_hunt:20}}
execute as @e[tag=ln_enemy,tag=rt_north,scores={ln_age=220}] run data merge entity @s {ForgeData:{ln_wp:[I;82,136,960],ln_wpr:3,ln_hunt:40}}
execute as @e[tag=ln_enemy,tag=rt_south,scores={ln_age=2}] run data merge entity @s {ForgeData:{ln_wp:[I;102,143,996],ln_wpr:3,ln_hunt:20}}
execute as @e[tag=ln_enemy,tag=rt_south,scores={ln_age=220}] run data merge entity @s {ForgeData:{ln_wp:[I;102,136,978],ln_wpr:3,ln_hunt:40}}
execute as @e[tag=ln_enemy,tag=rt_west,scores={ln_age=2}] run data merge entity @s {ForgeData:{ln_wp:[I;68,134,965],ln_wpr:3,ln_hunt:20}}
execute as @e[tag=ln_enemy,tag=rt_west,scores={ln_age=220}] run data merge entity @s {ForgeData:{ln_wp:[I;82,136,966],ln_wpr:3,ln_hunt:40}}
execute as @e[tag=ln_enemy,tag=rt_northeast,scores={ln_age=2}] run data merge entity @s {ForgeData:{ln_wp:[I;136,128,944],ln_wpr:3,ln_hunt:20}}
execute as @e[tag=ln_enemy,tag=rt_northeast,scores={ln_age=220}] run data merge entity @s {ForgeData:{ln_wp:[I;131,136,957],ln_wpr:3,ln_hunt:40}}
execute as @e[tag=ln_enemy,scores={ln_age=700}] run data merge entity @s {ForgeData:{ln_hunt:96}}
execute as @e[tag=ln_enemy,scores={ln_age=1800}] run effect give @s glowing 600 0 true
execute as @e[tag=ln_enemy,scores={ln_age=5000}] run kill @s
