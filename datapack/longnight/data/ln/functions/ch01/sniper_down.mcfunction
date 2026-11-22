# 由 tools/build_ch01.py 自動產生，請勿手動修改
execute as @e[tag=c1_sniper] at @s run particle minecraft:crit ~ ~1.6 ~ 0.2 0.2 0.2 0.2 20 force @a
playsound minecraft:entity.firework_rocket.blast master @a 100 120 1460 4 0.5
kill @e[tag=c1_sniper]
