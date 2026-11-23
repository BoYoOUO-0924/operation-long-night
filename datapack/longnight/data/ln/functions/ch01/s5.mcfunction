# 由 tools/build_ch01.py 自動產生，請勿手動修改
function ln:ch01/dlg/strike
execute if score #t ln matches 70 positioned 22 128 1300 unless entity @a[distance=..10] run function ln:ch01/strike_fx
execute if score #t ln matches 82 positioned 30 127 1330 unless entity @a[distance=..10] run function ln:ch01/strike_fx
execute if score #t ln matches 94 positioned 12 123 1340 unless entity @a[distance=..10] run function ln:ch01/strike_fx
execute if score #t ln matches 106 positioned 40 127 1290 unless entity @a[distance=..10] run function ln:ch01/strike_fx
execute if score #t ln matches 118 positioned 18 127 1318 unless entity @a[distance=..10] run function ln:ch01/strike_fx
execute if score #t ln matches 130 positioned 36 120 1350 unless entity @a[distance=..10] run function ln:ch01/strike_fx
execute if score #t ln matches 142 positioned 50 109 1372 unless entity @a[distance=..10] run function ln:ch01/strike_fx
execute if score #t ln matches 154 positioned 8 120 1310 unless entity @a[distance=..10] run function ln:ch01/strike_fx
execute if score #t ln matches 166 positioned 28 115 1280 unless entity @a[distance=..10] run function ln:ch01/strike_fx
execute if score #t ln matches 178 positioned 60 88 1400 unless entity @a[distance=..10] run function ln:ch01/strike_fx
execute if score #t ln matches 190 positioned 66 88 1430 unless entity @a[distance=..10] run function ln:ch01/strike_fx
execute if score #t ln matches 202 positioned 98 96 1450 unless entity @a[distance=..10] run function ln:ch01/strike_fx
execute if score #t ln matches 214 positioned 44 102 1386 unless entity @a[distance=..10] run function ln:ch01/strike_fx
execute if score #t ln matches 226 positioned 14 118 1296 unless entity @a[distance=..10] run function ln:ch01/strike_fx
execute if score #t ln matches 238 positioned 34 125 1312 unless entity @a[distance=..10] run function ln:ch01/strike_fx
execute if score #t ln matches 60 as @a at @s run playsound minecraft:entity.firework_rocket.launch master @s ~40 ~30 ~ 4 0.5
execute if score #t ln matches 130 run kill @e[tag=ln_enemy]
execute if score #t ln matches 120 run lnhud waypoint @a 22 111 1266
scoreboard players operation #tm ln = #t ln
scoreboard players set #k ln 30
scoreboard players operation #tm ln %= #k ln
execute if score #t ln matches 300..900 if score #tm ln matches 0 as @a at @s run playsound minecraft:entity.warden.heartbeat master @s ~ ~-6 ~ 2 0.5
execute if score #t ln matches 340..900 if score #tm ln matches 15 as @a at @s run playsound minecraft:block.beacon.ambient master @s ~ ~ ~ 1.5 0.5
execute if score #t ln matches 330..900 as @a at @s run particle minecraft:ash ~ ~1 ~ 6 2 6 0 4 normal @s
execute if score #t ln matches 420 run summon block_display 4 150 1430 {Tags:["ln","c1_glow"],brightness:{sky:15,block:15},block_state:{Name:"minecraft:light_blue_stained_glass"},Glowing:1b,glow_color_override:6737151,transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[-1f,-6f,-3f],scale:[2f,12f,6f]}}
execute if score #t ln matches 420 run particle minecraft:electric_spark 4 150 1430 2 6 3 0.4 200 force @a
execute if score #t ln matches 420 run lnhud tint @a 8060C0FF 30 flash
execute if score #t ln matches 450 run kill @e[tag=c1_glow]
execute if score #t ln matches 600 as @a at @s run playsound lnai:sfx.radio_off master @s ~ ~ ~ 1 0.8
execute if score #t ln matches 735 as @a at @s run playsound lnai:sfx.radio_on master @s ~ ~ ~ 1 0.7
execute if score #t ln matches 1320.. positioned 22 111 1266 if entity @a[gamemode=adventure,distance=..7] run function ln:ch01/arrive
