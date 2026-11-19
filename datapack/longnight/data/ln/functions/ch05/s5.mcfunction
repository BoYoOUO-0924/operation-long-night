# 由 tools/build_level.py 自動產生，請勿手動修改
function ln:ch05/dlg/combat_start
scoreboard players add @e[tag=ln_enemy] ln_age 1
function ln:ch05/dir/phase
execute store result score #alive ln if entity @e[tag=ln_enemy]
scoreboard players operation #left ln = #budget ln
scoreboard players operation #left ln += #alive ln
execute store result bossbar ln:obj value run scoreboard players get #left ln
bossbar set ln:obj name {"text": "", "font": "lnai:ui", "extra": [{"text": "敵軍剩餘兵力：", "color": "red"}, {"score": {"name": "#left", "objective": "ln"}, "color": "white"}, {"text": "　場上：", "color": "red"}, {"score": {"name": "#alive", "objective": "ln"}, "color": "white"}]}
scoreboard players add #dt ln 1
execute if score #final ln matches 0 if score #budget ln matches 7.. if score #dt ln matches 300.. if score #alive ln < #max ln run function ln:ch05/dir/spawn_next
execute if score #final ln matches 1 if score #budget ln matches 1.. if score #dt ln matches 300.. if score #alive ln < #max ln run function ln:ch05/dir/spawn_next
execute if score #budget ln matches 7.. if score #dt ln matches 120.. if score #alive ln matches ..3 run function ln:ch05/dir/spawn_next
execute if score #final ln matches 0 if score #budget ln matches ..6 if score #alive ln matches 0 run function ln:ch05/ev/final
scoreboard players add #pulse ln 1
execute if score #pulse ln matches 300.. run function ln:ch05/dir/pulse
execute if score #pulse ln matches 300.. run scoreboard players set #pulse ln 0
scoreboard players operation #pct ln = #total ln
scoreboard players operation #pct ln -= #left ln
scoreboard players set #k ln 100
scoreboard players operation #pct ln *= #k ln
scoreboard players operation #pct ln /= #total ln
execute if score #evgen ln matches 0 if score #pct ln matches 35.. run function ln:ch05/ev/gen_fail
execute if score #evgen ln matches 1 run function ln:ch05/ev/gen_tick
execute if score #final ln matches 0 if score #pct ln matches 65.. run function ln:ch05/ev/final
execute if score #tp ln matches 1.. run function ln:ch05/ev/drive
execute if score #mort ln matches 1.. run function ln:ch05/ev/mortar_tick
execute if score #mort ln matches ..0 if entity @e[tag=ln_mortar] run function ln:ch05/ev/mortar_tick
execute if score #final ln matches 1 if score #budget ln matches ..0 if score #alive ln matches 0 run function ln:ch05/to_s7
