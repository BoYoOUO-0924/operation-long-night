# 由 tools/build_level.py 自動產生，請勿手動修改
scoreboard players set #stage ln 2
scoreboard players set #t ln 0
execute as @e[tag=ln_ally] run data merge entity @s {ForgeData:{ln_follow:0b}}
tp @e[tag=ln_fox] 93 136 961
tp @e[tag=ln_tank] 90 136 962
tp @e[tag=ln_officer] 88 136 961
tp @e[tag=ln_baiya] 88 142 959
data merge entity @e[tag=ln_officer,limit=1] {NoAI:1b}
spawnpoint @a 104 136 965
effect clear @a slowness
bossbar set ln:obj name {"text": "目標：在車庫找到零件箱"}
bossbar set ln:obj color yellow
