# 由 tools/build_level.py 自動產生，請勿手動修改
lnhud music @a stop 60
lnhud ambient @a stop 60
kill @e[tag=ln]
scoreboard players set #stage ln 0
bossbar set ln:obj visible false
effect clear @a
schedule clear ln:ch05/evdlg/generator_fail_1
lnhud objective @a
gamerule naturalRegeneration true
