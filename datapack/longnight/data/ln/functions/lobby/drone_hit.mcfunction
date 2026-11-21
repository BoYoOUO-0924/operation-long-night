# 由 tools/build_lobby.py 自動產生，請勿手動修改
execute on attacker run scoreboard players add @s ln_hits 1
execute on attacker at @s run playsound minecraft:block.note_block.bell master @s ~ ~ ~ 1 1.6
execute on attacker run title @s actionbar [{"text": "命中靶機  ", "color": "#8EE07A", "font": "lnai:ui"}, {"score": {"name": "@s", "objective": "ln_hits"}, "color": "#F0E6C8", "font": "lnai:ui"}]
particle minecraft:flash ~ ~1 ~ 0 0 0 0 1 force
data modify entity @s Health set value 1000f
