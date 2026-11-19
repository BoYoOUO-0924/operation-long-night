# 由 tools/build_level.py 自動產生，請勿手動修改
tellraw @a [{"text": "▶ 目標：", "color": "yellow", "bold": true}, {"text": "到南邊的發電小屋拉起拉桿，重新啟動發電機！", "color": "white"}]
title @a actionbar {"text": "到南邊的發電小屋拉起拉桿，重新啟動發電機！", "color": "yellow"}
execute as @a at @s run playsound minecraft:block.note_block.bell master @s ~ ~ ~ 0.6 1.2
