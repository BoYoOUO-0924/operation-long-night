# 由 tools/build_level.py 自動產生，請勿手動修改
scoreboard players set #stage ln 4
scoreboard players set #t ln 0
function ln:ch05/ammo
bossbar set ln:obj name {"text": "準備防守：敵軍即將抵達"}
bossbar set ln:obj color red
bossbar set ln:obj max 400
