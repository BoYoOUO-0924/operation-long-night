# 由 tools/build_lobby.py 自動產生，請勿手動修改
tag @s remove ln_ready
tag @s remove ln_jumped
tag @s add ln_seen
gamemode adventure @s
clear @s
effect clear @s
lnkit restore @s none none
lnkit ammo @s 4 2 fill
function ln:lobby/kit_tags
scoreboard players set @s ln_hits 0
team join ln_blue @s
tp @s -301.5 273 916.5 180 0
spawnpoint @s -302 273 916
lnhud tint @s 00000000 40
lnhud objective @s 在作戰桌選擇章節，全員按「準備就緒」後出發
