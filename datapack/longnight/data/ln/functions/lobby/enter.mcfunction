# 由 tools/build_lobby.py 自動產生，請勿手動修改
scoreboard players set #c20 ln 20
execute unless score #placed ln matches 1 run function ln:lobby/place
forceload add -336 891 -268 962
lnhud cutscene @a stop
function ln:ch05/cleanup
scoreboard players set #lobby ln 1
scoreboard players set #inch ln 0
scoreboard players set #lt ln 0
time set 18000
weather clear
function ln:lobby/reset_jump
execute as @a run function ln:lobby/enter_one
function ln:lobby/anims
function ln:lobby/show_chap
