# 由 tools/build_level.py 自動產生，請勿手動修改
tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "▶ 目標：", "color": "yellow", "bold": true}, {"text": "守住氣象站! 撐到敵軍兵力耗盡。", "color": "white"}]}
lnhud objective @a 守住氣象站! 撐到敵軍兵力耗盡。
execute as @a at @s run playsound lnai:sfx.objective master @s ~ ~ ~ 0.8 1
lnhud waypoint @a clear
