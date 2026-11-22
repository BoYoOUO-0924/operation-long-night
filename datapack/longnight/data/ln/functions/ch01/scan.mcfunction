# 由 tools/build_ch01.py 自動產生，請勿手動修改
scoreboard players set #scan ln 1
execute as @a at @s run playsound lnai:sfx.scanner_pulse master @s ~ ~ ~ 0.7 1
execute positioned 73 96 1406 run effect give @e[tag=ln_enemy,distance=..70] glowing 6 0 true
