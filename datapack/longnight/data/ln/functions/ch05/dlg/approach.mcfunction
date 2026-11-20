# 由 tools/build_level.py 自動產生，請勿手動修改
execute if score #t ln matches 60 run lnhud say @a B4B4B4 150 "情報官" 我們……不能停下來休息嗎? 我真的走不動了。
execute if score #t ln matches 140 run lnhud say @a E0B050 120 "戰車" 走不動就用爬的。不想凍死就跟上。
execute if score #t ln matches 220 run lnhud say @a 8CC08C 235 "狐狸" 我的掃描器在海岸那次砲擊就壞了, 現在什麼都偵測不到。到站裡我得找零件修一修。
execute if score #t ln matches 340 run lnhud say @a 7FC8D8 115 "白鴉" 保持隊形, 從東側的車庫進去。
execute if score #t ln matches 400 run tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "▶ 目標：", "color": "yellow", "bold": true}, {"text": "沿著山坡往上走, 從氣象站東側的車庫進入。", "color": "white"}]}
execute if score #t ln matches 400 run lnhud objective @a 沿著山坡往上走, 從氣象站東側的車庫進入。
execute if score #t ln matches 400 run execute as @a at @s run playsound lnai:sfx.objective master @s ~ ~ ~ 0.8 1
execute if score #t ln matches 400 run lnhud waypoint @a 133 136 961
execute if score #t ln matches 1500 run tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "（提示）", "color": "dark_aqua"}, {"text": "氣象站在山坡上方（西邊）, 車庫門口有閃爍的琥珀色燈。", "color": "gray", "italic": true}]}
