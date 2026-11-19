tellraw @s {"text":"——— 長夜 標記工具箱 ———","color":"gold"}
tellraw @s [{"text":"站在想標記的位置，輸入：","color":"gray"}]
tellraw @s [{"text":" /function ln_tool:mark_trigger","color":"yellow"},{"text":"　走到這裡觸發劇情","color":"gray"}]
tellraw @s [{"text":" /function ln_tool:mark_enemy","color":"red"},{"text":"　敵人從這裡出現","color":"gray"}]
tellraw @s [{"text":" /function ln_tool:mark_ally","color":"aqua"},{"text":"　隊友站這裡","color":"gray"}]
tellraw @s [{"text":" /function ln_tool:mark_checkpoint","color":"green"},{"text":"　存檔點","color":"gray"}]
tellraw @s [{"text":" /function ln_tool:mark_camera","color":"light_purple"},{"text":"　過場鏡頭位置（面向你看的方向）","color":"gray"}]
tellraw @s [{"text":" /function ln_tool:mark_note","color":"white"},{"text":"　這裡有問題或想修改（再跟 Claude 說）","color":"gray"}]
tellraw @s [{"text":" /function ln_tool:undo","color":"gray"},{"text":"　刪除最近的標記　","color":"dark_gray"},{"text":"/function ln_tool:clear_all","color":"gray"},{"text":"　全部清除","color":"dark_gray"}]
tellraw @s {"text":"標好之後跟 Claude 說「標好了」，Claude 會讀取所有標記。","color":"gold"}
