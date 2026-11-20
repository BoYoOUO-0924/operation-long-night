# 由 tools/build_level.py 自動產生，請勿手動修改
tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "▶ 目標：", "color": "yellow", "bold": true}, {"text": "擊退主攻部隊! 注意地上的紅色標記, 那是砲彈落點。", "color": "white"}]}
lnhud objective @a 擊退主攻部隊! 注意地上的紅色標記, 那是砲彈落點。
execute as @a at @s run playsound lnai:sfx.objective master @s ~ ~ ~ 0.8 1
lnhud waypoint @a clear
