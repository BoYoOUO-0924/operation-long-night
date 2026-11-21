# 由 tools/build_lobby.py 自動產生，請勿手動修改
lnkit gun @s mk14 SCOPE=scope_acog_ta31
lnkit gun @s p320
item replace entity @s hotbar.2 with superbwarfare:knife
lnkit ammo @s 4 2 fill
playsound minecraft:item.armor.equip_iron master @s ~ ~ ~ 0.8 1.1
title @s actionbar {"text": "精確射手：MK14 ＋ P320", "color": "#8EE07A", "font": "lnai:ui"}
