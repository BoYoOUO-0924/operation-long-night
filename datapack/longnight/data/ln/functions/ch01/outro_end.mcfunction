# 由 tools/build_ch01.py 自動產生，請勿手動修改
lnhud tint @a FF000000 0
function ln:ch01/cleanup
scoreboard players set #done1 ln 1
scoreboard players set #run ln 0
bossbar set ln:obj visible false
lnhud objective @a
lnhud waypoint @a clear
schedule function ln:lobby/enter 40t replace
