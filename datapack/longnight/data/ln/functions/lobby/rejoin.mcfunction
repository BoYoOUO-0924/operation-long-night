# 由 tools/build_lobby.py 自動產生，請勿手動修改
scoreboard players reset @s ln_left
tag @s add ln_seen
execute if score #lobby ln matches 1.. run function ln:lobby/enter_one
execute if score #lobby ln matches 0 unless score #inch ln matches 1 if score #placed ln matches 1 run function ln:lobby/enter
