# 由 tools/build_level.py 自動產生，請勿手動修改
function ln:ch05/dlg/prepare
execute store result bossbar ln:obj value run scoreboard players get #t ln
execute if score #t ln matches 400 run function ln:ch05/to_s5
