# 由 tools/build_level.py 自動產生，請勿手動修改
scoreboard players set #stage ln 2
scoreboard players set #t ln 0
tp @e[tag=ln_fox] 109 137 954
tp @e[tag=ln_tank] 106 137 955
tp @e[tag=ln_officer] 104 137 954
tp @e[tag=ln_baiya] 104 143 952
spawnpoint @a 120 137 958
effect clear @a slowness
bossbar set ln:obj name {"text": "目標：在車庫找到零件箱"}
bossbar set ln:obj color yellow
