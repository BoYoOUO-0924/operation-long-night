# 由 tools/build_level.py 自動產生，請勿手動修改
execute if score #t ln matches 0 run tellraw @a [{"text": "▶ 目標：", "color": "yellow", "bold": true}, {"text": "準備防守氣象站！敵軍 20 秒後抵達。彈藥已補充。", "color": "white"}]
execute if score #t ln matches 0 run title @a actionbar {"text": "準備防守氣象站！敵軍 20 秒後抵達。彈藥已補充。", "color": "yellow"}
execute if score #t ln matches 0 run execute as @a at @s run playsound minecraft:block.note_block.bell master @s ~ ~ ~ 0.6 1.2
