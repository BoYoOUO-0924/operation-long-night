# 由 tools/build_level.py 自動產生，請勿手動修改
execute if score #wave ln matches 1 run function ln:ch05/dlg/wave1
execute if score #wave ln matches 2 run function ln:ch05/dlg/wave2
execute if score #wave ln matches 3 run function ln:ch05/dlg/wave3
execute store result score #enemies ln if entity @e[tag=ln_enemy]
execute store result bossbar ln:obj value run scoreboard players get #enemies ln
bossbar set ln:obj name [{"text": "第 ", "color": "red"}, {"score": {"name": "#wave", "objective": "ln"}, "color": "red"}, {"text": " / 3 波　剩餘敵人：", "color": "red"}, {"score": {"name": "#enemies", "objective": "ln"}, "color": "white"}]
execute if score #t ln matches 1800 run effect give @e[tag=ln_enemy] glowing 600 0 true
execute if score #t ln matches 1800 run tellraw @a {"text": "（提示）剩下的敵人已標示發光。", "color": "dark_aqua"}
execute if score #t ln matches 4800 run kill @e[tag=ln_enemy]
execute if score #t ln matches 60.. if score #enemies ln matches 0 run function ln:ch05/wave_cleared
