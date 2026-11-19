# 由 tools/build_level.py 自動產生，請勿手動修改
execute if score #tp ln matches 1 as @e[tag=ln_tech] at @s facing 160 130.2 962 run tp @s ^ ^ ^0.3
execute if score #tp ln matches 1 as @e[tag=ln_tech] at @s positioned 160 130 962 if entity @s[distance=..1.5] run scoreboard players add #tp ln 1
execute if score #tp ln matches 2 as @e[tag=ln_tech] at @s facing 156 132.2 962 run tp @s ^ ^ ^0.3
execute if score #tp ln matches 2 as @e[tag=ln_tech] at @s positioned 156 132 962 if entity @s[distance=..1.5] run scoreboard players add #tp ln 1
execute if score #tp ln matches 3 as @e[tag=ln_tech] at @s facing 152 133.2 962 run tp @s ^ ^ ^0.3
execute if score #tp ln matches 3 as @e[tag=ln_tech] at @s positioned 152 133 962 if entity @s[distance=..1.5] run scoreboard players add #tp ln 1
execute if score #tp ln matches 4 as @e[tag=ln_tech] at @s facing 148 133.2 962 run tp @s ^ ^ ^0.3
execute if score #tp ln matches 4 as @e[tag=ln_tech] at @s positioned 148 133 962 if entity @s[distance=..1.5] run scoreboard players add #tp ln 1
execute if score #tp ln matches 5 as @e[tag=ln_tech] at @s facing 144 133.2 962 run tp @s ^ ^ ^0.3
execute if score #tp ln matches 5 as @e[tag=ln_tech] at @s positioned 144 133 962 if entity @s[distance=..1.5] run scoreboard players add #tp ln 1
execute if score #tp ln matches 6 as @e[tag=ln_tech] at @s facing 140 133.2 962 run tp @s ^ ^ ^0.3
execute if score #tp ln matches 6 as @e[tag=ln_tech] at @s positioned 140 133 962 if entity @s[distance=..1.5] run scoreboard players add #tp ln 1
scoreboard players add #tpt ln 1
execute if score #tp ln matches 7.. run function ln:ch05/ev/tech_arrive
execute if score #tpt ln matches 400.. run function ln:ch05/ev/tech_arrive
