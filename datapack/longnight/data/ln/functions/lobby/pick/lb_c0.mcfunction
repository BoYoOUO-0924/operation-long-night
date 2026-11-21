# 由 tools/build_lobby.py 自動產生，請勿手動修改
lnkit gun @s hk416d SCOPE=sight_t2,GRIP=grip_vertical_military
lnkit gun @s glock_17
item replace entity @s hotbar.2 with superbwarfare:knife
lnkit ammo @s 4 2 fill
playsound minecraft:item.armor.equip_iron master @s ~ ~ ~ 0.8 1.1
title @s actionbar {"text": "突擊兵：HK416D ＋ Glock 17", "color": "#8EE07A", "font": "lnai:ui"}
