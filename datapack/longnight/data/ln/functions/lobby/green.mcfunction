# 由 tools/build_lobby.py 自動產生，請勿手動修改
setblock -309 276 943 verdant_froglight
setblock -295 276 943 verdant_froglight
fill -308 273 946 -296 273 946 air
lnhud tint @a 3010A040 6
schedule function ln:lobby/green_off 30t replace
lnhud objective @a 綠燈！從機尾跳下
execute as @a at @s run playsound lnai:sfx.scanner_ready master @s ~ ~ ~ 1 0.8
