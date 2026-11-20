# 由 tools/build_lobby.py 自動產生，請勿手動修改
function ln:lobby/clouds
scoreboard players add #lt ln 1
execute if score #lt ln matches 200.. run function ln:lobby/anims
execute if score #lt ln matches 200.. run scoreboard players set #lt ln 0
execute as @e[tag=lb_prev] if data entity @s interaction run function ln:lobby/sel_prev
execute as @e[tag=lb_next] if data entity @s interaction run function ln:lobby/sel_next
execute as @e[tag=lb_ready] if data entity @s interaction run function ln:lobby/click_ready
data remove entity @e[tag=lb_prev,limit=1] interaction
data remove entity @e[tag=lb_next,limit=1] interaction
data remove entity @e[tag=lb_ready,limit=1] interaction
execute store result score #pl ln if entity @a[gamemode=adventure]
execute store result score #rd ln if entity @a[gamemode=adventure,tag=ln_ready]
function ln:lobby/show_status
execute if score #lobby ln matches 1 if score #pl ln matches 1.. if score #rd ln = #pl ln run function ln:lobby/go
execute if score #lobby ln matches 1 as @a[x=-334,y=212,z=898,dx=64,dy=82,dz=58] at @s if entity @s[y=212,dy=57] run function ln:lobby/caught
execute if score #lobby ln matches 2 run function ln:lobby/jump_tick
