# 由 tools/build_level.py 自動產生，請勿手動修改
scoreboard players set #stage ln 3
scoreboard players set #t ln 0
bossbar set ln:obj name {"text": "（劇情）狐狸正在修理掃描器", "font": "lnai:ui"}
bossbar set ln:obj color yellow
execute positioned 93 136 961 run playsound minecraft:block.beacon.activate master @a ~ ~ ~ 1 1.5
