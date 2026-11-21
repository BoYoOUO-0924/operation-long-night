# 由 tools/build_lobby.py 自動產生，請勿手動修改
kill @e[tag=lb_drone_part]
execute as @e[tag=lb_drone] run data modify entity @s Size set value 0
tp @e[tag=lb_drone] ~ -200 ~
kill @e[tag=lb_drone]
