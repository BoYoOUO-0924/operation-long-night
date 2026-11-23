# 由 tools/build_ch01.py 自動產生，請勿手動修改
scoreboard players set #stage ln 0
scoreboard players set #done1 ln 1
bossbar set ln:obj visible false
lnhud objective @a
lnhud waypoint @a clear
lnhud title @a 100 FFFFB020 第一章　雷霆空降|任務完成・返回運輸機
lnhud music @a ch05_after 60
schedule function ln:ch01/to_lobby 140t replace
