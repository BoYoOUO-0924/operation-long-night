# 由 tools/build_level.py 自動產生，請勿手動修改
scoreboard players set #stage ln 0
scoreboard players set #done5 ln 1
bossbar set ln:obj visible false
lnhud objective @a
lnhud title @a 100 FFFFB020 第五章　寒霜陷阱|任務完成・返回運輸機
schedule function ln:ch05/to_lobby 140t replace
