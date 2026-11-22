# 由 tools/build_ch01.py 自動產生，請勿手動修改
scoreboard players set #stage ln 0
scoreboard players set #done1 ln 1
bossbar set ln:obj visible false
lnhud objective @a
lnhud waypoint @a clear
title @a times 20 100 30
title @a subtitle {"text": "任務完成・返回運輸機", "color": "gray", "font": "lnai:ui"}
title @a title {"text": "第一章　雷霆空降", "color": "gold", "bold": true, "font": "lnai:ui"}
lnhud music @a ch05_after 60
schedule function ln:ch01/to_lobby 140t replace
