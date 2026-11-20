# 由 tools/build_lobby.py 自動產生，請勿手動修改
scoreboard players add #jt ln 1
scoreboard players operation #jm ln = #jt ln
scoreboard players operation #jm ln %= #c20 ln
execute if score #jm ln matches 0 as @a at @s run playsound lnai:sfx.jump_alarm master @s ~ ~ ~ 0.7 1
execute if score #jt ln matches 100 run function ln:lobby/green
execute if score #jt ln matches ..99 as @a[x=-334,y=212,z=898,dx=64,dy=82,dz=58] at @s if entity @s[y=212,dy=57] run function ln:lobby/caught
execute if score #jt ln matches 100.. as @a[x=-334,y=212,z=898,dx=64,dy=82,dz=58,tag=!ln_jumped] at @s if entity @s[y=212,dy=57] run function ln:lobby/jumped
execute store result score #jd ln if entity @a[gamemode=adventure,tag=ln_jumped]
execute if score #jd ln = #pl ln unless score #jw ln matches 1.. run scoreboard players set #jw ln 1
execute if score #jw ln matches 1.. run scoreboard players add #jw ln 1
execute if score #jw ln matches 22.. run function ln:lobby/launch_now
execute if score #jt ln matches 700.. run function ln:lobby/launch_now
