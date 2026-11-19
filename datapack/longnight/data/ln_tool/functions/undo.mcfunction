# 刪除離你最近（5 格內）的一個標記
execute as @e[type=marker,tag=ln_mark,distance=..5,sort=nearest,limit=1] at @s run kill @e[type=text_display,tag=ln_mark_label,distance=..2]
kill @e[type=marker,tag=ln_mark,distance=..5,sort=nearest,limit=1]
tellraw @s {"text":"[標記] 已刪除最近的標記","color":"gray"}
