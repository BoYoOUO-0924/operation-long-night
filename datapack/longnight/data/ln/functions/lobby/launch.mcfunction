# 由 tools/build_lobby.py 自動產生，請勿手動修改
scoreboard players set #lobby ln 0
scoreboard players set #inch ln 1
function ln:lobby/reset_jump
tag @a remove ln_ready
tag @a remove ln_jumped
effect clear @a
execute if score #chap ln matches 5 run function ln:ch05/start
lnhud tint @a 00000000 30
forceload remove -336 891 -268 962
