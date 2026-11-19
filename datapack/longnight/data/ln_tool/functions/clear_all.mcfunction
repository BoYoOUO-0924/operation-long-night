kill @e[type=marker,tag=ln_mark]
kill @e[type=text_display,tag=ln_mark_label]
scoreboard players set #mark_next ln 0
tellraw @s {"text":"[標記] 已清除所有標記","color":"gray"}
