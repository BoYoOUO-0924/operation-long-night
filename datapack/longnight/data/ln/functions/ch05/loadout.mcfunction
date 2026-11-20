# 由 tools/build_level.py 自動產生，請勿手動修改
item replace entity @a[gamemode=adventure] hotbar.0 with tacz:modern_kinetic_gun{GunId:"tacz:m4a1",GunCurrentAmmoCount:30,HasBulletInBarrel:1b}
item replace entity @a[gamemode=adventure] hotbar.1 with tacz:modern_kinetic_gun{GunId:"tacz:glock_17",GunCurrentAmmoCount:17,HasBulletInBarrel:1b}
item replace entity @a[gamemode=adventure] hotbar.2 with superbwarfare:knife
item replace entity @a[gamemode=adventure] hotbar.3 with superbwarfare:hand_grenade 2
item replace entity @a[gamemode=adventure] hotbar.4 with lnai:bandage 4
function ln:ch05/ammo
give @a[gamemode=adventure] lnai:painkiller 2
give @a[gamemode=adventure] lnai:medkit 2
give @a[gamemode=adventure] superbwarfare:rgo_grenade 1
give @a[gamemode=adventure] superbwarfare:m18_smoke_grenade 1
item replace entity @a[gamemode=adventure] armor.head with zerocontact:helmet_airframe
item replace entity @a[gamemode=adventure] armor.chest with zerocontact:armor_defender_2
effect give @a[gamemode=adventure] saturation infinite 0 true
