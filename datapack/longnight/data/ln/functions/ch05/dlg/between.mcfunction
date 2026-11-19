# 由 tools/build_level.py 自動產生，請勿手動修改
execute if score #t ln matches 20 run tellraw @a [{"text": "[狐狸] ", "color": "green", "bold": true}, {"text": "這波清掉了。下一批正在集結，趁現在補彈藥！", "color": "white"}]
execute if score #t ln matches 20 run execute as @a at @s run playsound minecraft:ui.button.click master @s ~ ~ ~ 0.3 1.8
