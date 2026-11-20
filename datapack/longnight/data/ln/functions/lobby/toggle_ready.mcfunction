# 由 tools/build_lobby.py 自動產生，請勿手動修改
execute on target if entity @s[tag=ln_ready] run tag @s add ln_unready
execute on target if entity @s[tag=!ln_ready] run tag @s add ln_ready
execute on target if entity @s[tag=ln_unready] run tag @s remove ln_ready
execute on target run tag @s remove ln_unready
execute on target at @s run playsound lnai:sfx.scanner_ready master @s ~ ~ ~ 0.6 1
