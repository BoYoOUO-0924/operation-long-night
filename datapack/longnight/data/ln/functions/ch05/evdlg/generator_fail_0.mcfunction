# 由 tools/build_level.py 自動產生，請勿手動修改
tellraw @a [{"text": "[狐狸] ", "color": "green", "bold": true}, {"text": "發電機停了！鍋爐的循環泵沒電，這裡很快就會結冰！", "color": "white"}]
execute as @a at @s run playsound minecraft:ui.button.click master @s ~ ~ ~ 0.3 1.8
