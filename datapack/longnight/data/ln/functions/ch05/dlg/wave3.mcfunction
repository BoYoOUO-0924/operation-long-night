# 由 tools/build_level.py 自動產生，請勿手動修改
execute if score #t ln matches 0 run tellraw @a [{"text": "[戰車] ", "color": "gold", "bold": true}, {"text": "這是主力部隊！撐住，撐過這一波就好！", "color": "white"}]
execute if score #t ln matches 0 run execute as @a at @s run playsound minecraft:ui.button.click master @s ~ ~ ~ 0.3 1.8
execute if score #t ln matches 60 run tellraw @a [{"text": "[白鴉] ", "color": "aqua", "bold": true}, {"text": "西側高地有狙擊手，注意窗戶！", "color": "white"}]
execute if score #t ln matches 60 run execute as @a at @s run playsound minecraft:ui.button.click master @s ~ ~ ~ 0.3 1.8
