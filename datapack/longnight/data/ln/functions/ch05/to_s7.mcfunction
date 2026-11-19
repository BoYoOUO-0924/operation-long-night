# 由 tools/build_level.py 自動產生，請勿手動修改
scoreboard players set #stage ln 7
scoreboard players set #t ln 0
bossbar set ln:obj name {"text": "防守成功"}
bossbar set ln:obj color green
bossbar set ln:obj value 0
kill @e[tag=ln_tech]
kill @e[tag=ln_mortar]
