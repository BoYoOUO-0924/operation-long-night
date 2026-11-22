# 由 tools/build_ch01.py 自動產生，請勿手動修改
lnhud music @a stop 60
lnhud ambient @a stop 60
kill @e[tag=ln]
lnglass restore
scoreboard players set #stage ln 0
scoreboard players set #run ln 0
bossbar set ln:obj visible false
effect clear @a
tag @a remove c1_chute
lnhud objective @a
lnhud waypoint @a clear
gamerule naturalRegeneration true
schedule clear ln:ch01/to_lobby
schedule clear ln:ch01/sniper_down
