# 由 tools/build_lobby.py 自動產生，請勿手動修改
scoreboard players add #chap ln 1
execute if score #chap ln matches 9.. run scoreboard players set #chap ln 1
function ln:lobby/show_chap
execute as @a at @s run playsound lnai:sfx.objective master @s ~ ~ ~ 0.4 1.4
