# 由 tools/build_level.py 自動產生，請勿手動修改
execute if score #t ln matches 0 run tellraw @a [{"text": "[狐狸] ", "color": "green", "bold": true}, {"text": "北邊和南邊同時出現訊號！他們要包夾我們！", "color": "white"}]
execute if score #t ln matches 0 run execute as @a at @s run playsound minecraft:ui.button.click master @s ~ ~ ~ 0.3 1.8
