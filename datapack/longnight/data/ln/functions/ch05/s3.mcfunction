# 由 tools/build_level.py 自動產生，請勿手動修改
function ln:ch05/dlg/reveal
execute if score #t ln matches 180 run effect give @e[tag=ln_officer] glowing 12 0 true
execute if score #t ln matches 180 as @a at @s run playsound lnai:sfx.scanner_pulse master @s ~ ~ ~ 1 1.35
execute if score #t ln matches 1140 run function ln:ch05/to_s4
