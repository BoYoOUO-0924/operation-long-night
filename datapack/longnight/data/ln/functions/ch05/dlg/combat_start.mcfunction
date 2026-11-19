# 由 tools/build_level.py 自動產生，請勿手動修改
execute if score #t ln matches 0 run tellraw @a [{"text": "[白鴉] ", "color": "aqua", "bold": true}, {"text": "來了。第一組人從山下上來。", "color": "white"}]
execute if score #t ln matches 0 run execute as @a at @s run playsound minecraft:ui.button.click master @s ~ ~ ~ 0.3 1.8
