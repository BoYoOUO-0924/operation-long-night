# 由 tools/build_lobby.py 自動產生，請勿手動修改
setblock -302 280 910 shroomlight
setblock -302 280 914 shroomlight
setblock -302 280 918 shroomlight
setblock -302 280 922 shroomlight
setblock -302 280 926 shroomlight
setblock -302 280 930 shroomlight
setblock -302 280 934 shroomlight
setblock -302 280 938 shroomlight
setblock -302 280 942 shroomlight
scoreboard players set #lobby ln 2
scoreboard players set #jt ln 0
scoreboard players set #jw ln 0
setblock -309 276 942 shroomlight
setblock -295 276 942 shroomlight
fill -309 272 949 -295 272 952 polished_andesite
fill -309 273 949 -309 273 952 iron_bars
fill -295 273 949 -295 273 952 iron_bars
lnhud tint @a 55B01010 30 pulse
lnhud objective @a 戰鬥紅光：到機尾待命，跳傘燈轉綠就跳
execute as @a at @s run playsound minecraft:block.piston.contract master @s ~ ~ ~ 1 0.5
