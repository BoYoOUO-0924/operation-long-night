execute store result score #total bf_count if entity @e[type=tacznpcs:npc]
tellraw @a [{"text":"[大戰場測試] 目前 NPC 數量：","color":"aqua"},{"score":{"name":"#total","objective":"bf_count"},"color":"yellow"}]
