# 由 tools/build_level.py 自動產生，請勿手動修改
execute if score #t ln matches 60 run tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "[情報官] ", "color": "gray", "bold": true}, {"text": "我們……不能停下來休息嗎? 我真的走不動了。", "color": "white"}]}
execute if score #t ln matches 60 run execute as @a at @s run playsound minecraft:ui.button.click master @s ~ ~ ~ 0.3 1.8
execute if score #t ln matches 140 run tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "[戰車] ", "color": "gold", "bold": true}, {"text": "走不動就用爬的。不想凍死就跟上。", "color": "white"}]}
execute if score #t ln matches 140 run execute as @a at @s run playsound minecraft:ui.button.click master @s ~ ~ ~ 0.3 1.8
execute if score #t ln matches 220 run tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "[狐狸] ", "color": "green", "bold": true}, {"text": "我的掃描器在海岸那次砲擊就壞了, 現在什麼都偵測不到。到站裡我得找零件修一修。", "color": "white"}]}
execute if score #t ln matches 220 run execute as @a at @s run playsound minecraft:ui.button.click master @s ~ ~ ~ 0.3 1.8
execute if score #t ln matches 340 run tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "[白鴉] ", "color": "aqua", "bold": true}, {"text": "保持隊形, 從東側的車庫進去。", "color": "white"}]}
execute if score #t ln matches 340 run execute as @a at @s run playsound minecraft:ui.button.click master @s ~ ~ ~ 0.3 1.8
execute if score #t ln matches 400 run tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "▶ 目標：", "color": "yellow", "bold": true}, {"text": "沿著山坡往上走, 從氣象站東側的車庫進入。", "color": "white"}]}
execute if score #t ln matches 400 run lnhud objective @a 沿著山坡往上走, 從氣象站東側的車庫進入。
execute if score #t ln matches 400 run execute as @a at @s run playsound minecraft:block.note_block.bell master @s ~ ~ ~ 0.6 1.2
execute if score #t ln matches 400 run lnhud waypoint @a 133 136 961
execute if score #t ln matches 1500 run tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "（提示）", "color": "dark_aqua"}, {"text": "氣象站在山坡上方（西邊）, 車庫門口有閃爍的琥珀色燈。", "color": "gray", "italic": true}]}
