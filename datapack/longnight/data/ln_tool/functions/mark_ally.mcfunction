# 在你腳下放一個「✚ 隊友位置」標記（浮空文字 + 記錄座標用的 marker）
scoreboard players add #mark_next ln 1
summon marker ~ ~ ~ {Tags:["ln_mark","ln_mark_new","ln_mark_ally"],data:{type:"ally"}}
execute as @e[type=marker,tag=ln_mark_new] store result entity @s data.id int 1 run scoreboard players get #mark_next ln
execute as @e[tag=ln_mark_new] run tp @s ~ ~ ~ ~ ~
tag @e[tag=ln_mark_new] remove ln_mark_new
summon text_display ~ ~1.3 ~ {Tags:["ln_mark_label"],billboard:"center",see_through:1b,text:'{"text":"✚ 隊友位置","color":"aqua","bold":true}'}
tellraw @s [{"text":"[標記] 已放置 ","color":"gray"},{"text":"✚ 隊友位置 #","color":"aqua"},{"score":{"name":"#mark_next","objective":"ln"},"color":"aqua"},{"text":"　（復原：/function ln_tool:undo）","color":"dark_gray"}]
playsound minecraft:block.note_block.chime master @s ~ ~ ~ 0.6 1.5
