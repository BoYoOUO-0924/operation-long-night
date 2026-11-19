# 由 tools/build_level.py 自動產生，請勿手動修改
function ln:ch05/dlg/approach
effect give @a[gamemode=adventure] slowness 2 0 true
execute at @a run particle minecraft:snowflake ~ ~2 ~ 6 2 6 0.02 25 normal @a
execute positioned 149 137 954 if entity @a[gamemode=adventure,distance=..9] run function ln:ch05/to_s2
