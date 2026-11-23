# 由 tools/build_ch01.py 自動產生，請勿手動修改
scoreboard players set @s ln_lit -60
effect give @s glowing 5 0 true
playsound lnai:sfx.jump_alarm master @s ~ ~ ~ 0.8 1.3
particle minecraft:explosion ~ ~1 ~ 4 3 4 0 5 force @a
particle minecraft:large_smoke ~ ~1 ~ 4 3 4 0.02 30 force @a
playsound minecraft:entity.generic.explode master @a ~ ~ ~ 3 0.8
lnhud tint @s 60FFFFFF 12 flash
damage @s 2 minecraft:explosion
execute if score #litsaid ln matches 0 run function ln:ch01/evdlg/evt_lit
scoreboard players set #litsaid ln 1
