# 長夜：載入時初始化（不會重置進行中的關卡）
scoreboard objectives add ln dummy
scoreboard objectives add ln_mark dummy
bossbar add ln:obj ""
gamerule doMobSpawning false
gamerule keepInventory true
gamerule doImmediateRespawn true
gamerule doDaylightCycle false
gamerule doWeatherCycle false
gamerule doFireTick false
gamerule mobGriefing false
gamerule announceAdvancements false
tellraw @a [{"text":"[長夜] ","color":"gold"},{"text":"已載入。開始試做關卡：","color":"gray"},{"text":"/function ln:ch05/start","color":"yellow"},{"text":"　標記工具：","color":"gray"},{"text":"/function ln_tool:help","color":"yellow"}]
