# 由 tools/build_ch01.py 自動產生，請勿手動修改
particle minecraft:explosion_emitter ~ ~1 ~ 1 1 1 0 2 force @a
particle minecraft:large_smoke ~ ~1 ~ 1.5 1.5 1.5 0.05 40 force @a
particle minecraft:lava ~ ~1 ~ 1 1 1 0 20 force @a
playsound lnai:sfx.boom master @a ~ ~1 ~ 6 0.9
playsound minecraft:entity.generic.explode master @a ~ ~1 ~ 4 0.7
particle minecraft:flash ~ ~2 ~ 0 0 0 0 1 force @a
execute as @a[distance=..40] run lnhud tint @s 40FFD0A0 6 pulse
