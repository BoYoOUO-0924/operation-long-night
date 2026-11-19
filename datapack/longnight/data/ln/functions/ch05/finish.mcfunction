# 由 tools/build_level.py 自動產生，請勿手動修改
scoreboard players set #stage ln 0
bossbar set ln:obj visible false
title @a times 20 100 30
title @a subtitle {"text": "感謝遊玩！把感想告訴 Claude 吧", "color": "gray", "font": "lnai:ui"}
title @a title {"text": "試做關卡完成", "color": "gold", "bold": true, "font": "lnai:ui"}
tellraw @a {"text": "[長夜] 重玩：/function ln:ch05/start　　中止：/function ln:ch05/stop", "color": "gold", "font": "lnai:ui"}
