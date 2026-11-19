# 長夜：載入時初始化（不會重置進行中的關卡）
scoreboard objectives add ln dummy
scoreboard objectives add ln_mark dummy
scoreboard objectives add ln_age dummy
bossbar add ln:obj ""
team add ln_blue
team modify ln_blue color aqua
team modify ln_blue friendlyFire false
team modify ln_blue seeFriendlyInvisibles true
team add ln_red
team modify ln_red color red
gamerule doMobSpawning false
gamerule keepInventory true
gamerule doImmediateRespawn true
gamerule doDaylightCycle false
gamerule doWeatherCycle false
gamerule doFireTick false
gamerule mobGriefing false
gamerule announceAdvancements false
tellraw @a [{"text":"[長夜] ","color":"gold"},{"text":"已載入。開始試做關卡：","color":"gray"},{"text":"/function ln:ch05/start","color":"yellow"},{"text":"　標記工具：","color":"gray"},{"text":"/function ln_tool:help","color":"yellow"}]
