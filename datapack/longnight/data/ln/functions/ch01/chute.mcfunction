# 由 tools/build_ch01.py 自動產生，請勿手動修改
execute as @a[tag=c1_chute,scores={ln_pid=1}] at @s run tp @e[tag=c1_chute_1] ~ ~ ~ ~ 0
execute as @a[tag=c1_chute,scores={ln_pid=2}] at @s run tp @e[tag=c1_chute_2] ~ ~ ~ ~ 0
execute as @a[tag=c1_chute,scores={ln_pid=3}] at @s run tp @e[tag=c1_chute_3] ~ ~ ~ ~ 0
execute as @a[tag=c1_chute,scores={ln_pid=4}] at @s run tp @e[tag=c1_chute_4] ~ ~ ~ ~ 0
execute as @a[tag=c1_chute] at @s if block ~ ~ ~ water run tp @s 92 64 1414
execute as @a[tag=c1_chute] at @s unless block ~ ~-0.3 ~ air unless block ~ ~-0.3 ~ water run function ln:ch01/land
