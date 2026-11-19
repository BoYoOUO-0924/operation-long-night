# 由 tools/build_level.py 自動產生，請勿手動修改
tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "[狐狸] ", "color": "green", "bold": true}, {"text": "電力恢復！鍋爐重新運轉了，幹得好！", "color": "white"}]}
execute as @a at @s run playsound minecraft:ui.button.click master @s ~ ~ ~ 0.3 1.8
