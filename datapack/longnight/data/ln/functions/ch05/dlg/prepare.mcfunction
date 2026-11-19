# 由 tools/build_level.py 自動產生，請勿手動修改
execute if score #t ln matches 0 run tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "▶ 目標：", "color": "yellow", "bold": true}, {"text": "守住氣象站！撐到敵軍兵力耗盡。彈藥已補充。", "color": "white"}]}
execute if score #t ln matches 0 run lnhud objective @a 守住氣象站！撐到敵軍兵力耗盡。彈藥已補充。
execute if score #t ln matches 0 run execute as @a at @s run playsound minecraft:block.note_block.bell master @s ~ ~ ~ 0.6 1.2
execute if score #t ln matches 0 run lnhud waypoint @a clear
execute if score #t ln matches 60 run tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "[狐狸] ", "color": "green", "bold": true}, {"text": "掃描器每 15 秒掃一次，我會報敵人的方向。", "color": "white"}]}
execute if score #t ln matches 60 run execute as @a at @s run playsound minecraft:ui.button.click master @s ~ ~ ~ 0.3 1.8
execute if score #t ln matches 160 run tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "[戰車] ", "color": "gold", "bold": true}, {"text": "我守車庫大門，狐狸顧西門。白鴉，塔上交給你。", "color": "white"}]}
execute if score #t ln matches 160 run execute as @a at @s run playsound minecraft:ui.button.click master @s ~ ~ ~ 0.3 1.8
