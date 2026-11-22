# 由 tools/build_ch01.py 自動產生，請勿手動修改
execute if score #t ln matches 40 run tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "▶ 目標：", "color": "yellow", "bold": true}, {"text": "炸毀三座雷達: 在雷達底座安裝 C4, 守住到引爆。", "color": "white"}]}
execute if score #t ln matches 40 run lnhud objective @a 炸毀三座雷達: 在雷達底座安裝 C4, 守住到引爆。
execute if score #t ln matches 40 run execute as @a at @s run playsound lnai:sfx.objective master @s ~ ~ ~ 0.8 1
execute if score #t ln matches 80 run lnhud say @a 8CC08C 165 "狐狸" 三座我都標在羅盤上了。分頭還是一起, 隊長你決定。
execute if score #t ln matches 180 run lnhud say @a E0B050 135 "戰車" 一起啦, 分頭行動的都死在電影第一幕。
