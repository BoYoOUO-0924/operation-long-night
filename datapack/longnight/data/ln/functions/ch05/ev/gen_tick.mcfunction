# 由 tools/build_level.py 自動產生，請勿手動修改
scoreboard players add #gent ln 1
particle minecraft:campfire_signal_smoke 112 146 982 0.2 0.5 0.2 0.01 2 force @a
particle minecraft:electric_spark 112.5 145.3 982.5 0.15 0.15 0.15 0.05 3 force @a
execute if score #gent ln matches 1200.. run scoreboard players operation #gm ln = #gent ln
execute if score #gent ln matches 1200.. run scoreboard players operation #gm ln %= #c100 ln
execute if score #gent ln matches 1200.. if score #gm ln matches 0 run effect give @a[gamemode=adventure] slowness 6 0 true
execute if score #gent ln matches 1200.. if score #gm ln matches 0 run effect give @a[gamemode=adventure] mining_fatigue 6 0 true
execute if score #gent ln matches 1200 run function ln:ch05/evdlg/generator_cold
execute if block 112 145 982 lever[powered=true] run function ln:ch05/ev/gen_fixed
