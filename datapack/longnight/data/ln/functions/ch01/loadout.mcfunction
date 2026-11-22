# 由 tools/build_ch01.py 自動產生，請勿手動修改
lnkit restore @a[gamemode=adventure] m4a1 glock_17
item replace entity @a[gamemode=adventure] hotbar.2 with superbwarfare:knife
item replace entity @a[gamemode=adventure] hotbar.3 with superbwarfare:hand_grenade 2
item replace entity @a[gamemode=adventure] hotbar.4 with lnai:bandage 4
lnkit ammo @a[gamemode=adventure] 4 2 add
give @a[gamemode=adventure] lnai:painkiller 2
give @a[gamemode=adventure] lnai:medkit 2
give @a[gamemode=adventure] superbwarfare:m18_smoke_grenade 1
item replace entity @a[gamemode=adventure] armor.head with zerocontact:helmet_airframe
item replace entity @a[gamemode=adventure] armor.chest with zerocontact:armor_defender_2
effect give @a[gamemode=adventure] saturation infinite 0 true
execute as @a[gamemode=adventure] run function ln:lobby/kit_extras
