# 由 tools/build_level.py 自動產生，請勿手動修改
function ln:ch05/dlg/arrival
execute if score #t ln matches 600.. run particle minecraft:happy_villager 144 138 960 0.3 0.3 0.3 0 2 force @a
execute if score #t ln matches 40.. if block 144 138 960 minecraft:stone_button[powered=true] run function ln:ch05/to_s3
