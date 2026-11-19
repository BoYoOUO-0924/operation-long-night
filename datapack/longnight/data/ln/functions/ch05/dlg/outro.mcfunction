# 由 tools/build_level.py 自動產生，請勿手動修改
execute if score #t ln matches 40 run tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "[白鴉] ", "color": "aqua", "bold": true}, {"text": "……熱源在後撤。他們退了。", "color": "white"}]}
execute if score #t ln matches 40 run execute as @a at @s run playsound minecraft:ui.button.click master @s ~ ~ ~ 0.3 1.8
execute if score #t ln matches 120 run tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "[狐狸] ", "color": "green", "bold": true}, {"text": "不是撤退，是重新部署。守夜人知道我們在這裡，我們得在天亮前離開。", "color": "white"}]}
execute if score #t ln matches 120 run execute as @a at @s run playsound minecraft:ui.button.click master @s ~ ~ ~ 0.3 1.8
execute if score #t ln matches 240 run tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "[戰車] ", "color": "gold", "bold": true}, {"text": "（對情報官）你給我聽好，你的命現在是我的。開門之前敢耍花樣，我第一個斃了你。", "color": "white"}]}
execute if score #t ln matches 240 run execute as @a at @s run playsound minecraft:ui.button.click master @s ~ ~ ~ 0.3 1.8
execute if score #t ln matches 360 run tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "[情報官] ", "color": "gray", "bold": true}, {"text": "……我明白。", "color": "white"}]}
execute if score #t ln matches 360 run execute as @a at @s run playsound minecraft:ui.button.click master @s ~ ~ ~ 0.3 1.8
execute if score #t ln matches 440 run tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "[狐狸] ", "color": "green", "bold": true}, {"text": "方舟的入口就在這座山底下。下一站——地下。", "color": "white"}]}
execute if score #t ln matches 440 run execute as @a at @s run playsound minecraft:ui.button.click master @s ~ ~ ~ 0.3 1.8
