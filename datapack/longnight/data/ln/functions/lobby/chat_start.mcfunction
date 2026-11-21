# 由 tools/build_lobby.py 自動產生，請勿手動修改
scoreboard players set #ct ln 1
scoreboard players add #cv ln 1
execute if score #cv ln matches 7.. run scoreboard players set #cv ln 1
