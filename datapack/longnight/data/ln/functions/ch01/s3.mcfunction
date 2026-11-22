# 由 tools/build_ch01.py 自動產生，請勿手動修改
execute store result bossbar ln:obj value run scoreboard players get #t ln
execute if score #t ln matches 1.. run particle minecraft:electric_spark 49 111 1373 0.2 0.2 0.2 0.1 2 force @a
scoreboard players operation #tm ln = #t ln
scoreboard players operation #tm ln %= #c20 ln
execute if score #tm ln matches 0 run playsound minecraft:block.note_block.hat master @a 49 111 1373 1.5 1.8
execute if score #t ln matches 200 run function ln:ch01/gate_open
