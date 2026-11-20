# 由 tools/build_level.py 自動產生，請勿手動修改
execute if score #t ln matches 20 run lnhud say @a 8CC08C 240 "狐狸" МЕТЕОСТАНЦИЯ №7……蘇聯時期的高山氣象站。發電機早就停了, 但地熱鍋爐好像還在運轉。
execute if score #t ln matches 20 run execute as @a at @s run playsound minecraft:ui.button.click master @s ~ ~ ~ 0.3 1.8
execute if score #t ln matches 120 run lnhud say @a E0B050 155 "戰車" 總算有點溫度了。我先把這傢伙帶進無線電室看著。
execute if score #t ln matches 120 run execute as @a at @s run playsound minecraft:ui.button.click master @s ~ ~ ~ 0.3 1.8
execute if score #t ln matches 200 run lnhud say @a 7FC8D8 170 "白鴉" 我上瞭望塔。這種天氣什麼都看不清楚, 但總比沒有好。
execute if score #t ln matches 200 run execute as @a at @s run playsound minecraft:ui.button.click master @s ~ ~ ~ 0.3 1.8
execute if score #t ln matches 280 run lnhud say @a 8CC08C 175 "狐狸" 車庫裡應該有備用零件箱。幫我找找看, 箱子上有個按鈕。
execute if score #t ln matches 280 run execute as @a at @s run playsound minecraft:ui.button.click master @s ~ ~ ~ 0.3 1.8
execute if score #t ln matches 320 run tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "▶ 目標：", "color": "yellow", "bold": true}, {"text": "在車庫找到零件箱, 按下上面的按鈕。", "color": "white"}]}
execute if score #t ln matches 320 run lnhud objective @a 在車庫找到零件箱, 按下上面的按鈕。
execute if score #t ln matches 320 run execute as @a at @s run playsound minecraft:block.note_block.bell master @s ~ ~ ~ 0.6 1.2
execute if score #t ln matches 320 run lnhud waypoint @a 128 137 967
execute if score #t ln matches 900 run tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "（提示）", "color": "dark_aqua"}, {"text": "零件箱在車庫北側角落, 有綠色光點標示。", "color": "gray", "italic": true}]}
