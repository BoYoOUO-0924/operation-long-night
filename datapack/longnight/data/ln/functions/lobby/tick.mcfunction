# 由 tools/build_lobby.py 自動產生，請勿手動修改
execute as @a[tag=!ln_seen] run function ln:lobby/rejoin
execute as @a[scores={ln_left=1..}] run function ln:lobby/rejoin
execute if score #lobby ln matches 1.. run function ln:lobby/active
