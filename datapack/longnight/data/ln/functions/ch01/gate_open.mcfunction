# 由 tools/build_ch01.py 自動產生，請勿手動修改
fill 41 110 1372 47 114 1372 air
playsound minecraft:block.iron_door.open master @a 49 111 1373 3 0.5
playsound minecraft:block.piston.contract master @a 49 111 1373 3 0.6
function ln:ch01/evdlg/evt_gate_open
execute as @e[tag=ln_fox] run data merge entity @s {ForgeData:{ln_follow:1b}}
function ln:ch01/to_s4
