# 由 tools/build_level.py 自動產生，請勿手動修改
execute positioned 107 136 965 run effect give @e[tag=ln_enemy,distance=..90] glowing 3 0 true
execute as @a at @s run playsound minecraft:block.beacon.power_select master @s ~ ~ ~ 0.5 1.8
execute store result score #q0 ln if entity @e[tag=ln_enemy,x=17,y=60,z=875,dx=180,dy=160,dz=74]
execute store result score #q1 ln if entity @e[tag=ln_enemy,x=17,y=60,z=981,dx=180,dy=160,dz=74]
execute store result score #q2 ln if entity @e[tag=ln_enemy,x=131,y=60,z=949,dx=70,dy=160,dz=32]
execute store result score #q3 ln if entity @e[tag=ln_enemy,x=17,y=60,z=949,dx=66,dy=160,dz=32]
execute if entity @e[tag=ln_enemy] run tellraw @a [{"text": "[狐狸] ", "color": "green", "bold": true}, {"text": "掃描：", "color": "white"}, {"text": "北 ", "color": "gray"}, {"score": {"name": "#q0", "objective": "ln"}, "color": "yellow"}, {"text": "　", "color": "gray"}, {"text": "南 ", "color": "gray"}, {"score": {"name": "#q1", "objective": "ln"}, "color": "yellow"}, {"text": "　", "color": "gray"}, {"text": "東 ", "color": "gray"}, {"score": {"name": "#q2", "objective": "ln"}, "color": "yellow"}, {"text": "　", "color": "gray"}, {"text": "西 ", "color": "gray"}, {"score": {"name": "#q3", "objective": "ln"}, "color": "yellow"}, {"text": "　", "color": "gray"}]
