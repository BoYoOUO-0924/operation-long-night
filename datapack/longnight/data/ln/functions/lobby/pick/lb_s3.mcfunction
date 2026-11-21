# 由 tools/build_lobby.py 自動產生，請勿手動修改
scoreboard players add @s ln_kit 1
execute if score @s ln_kit matches 4.. run scoreboard players set @s ln_kit 1
function ln:lobby/kit_tags
playsound minecraft:item.armor.equip_leather master @s ~ ~ ~ 0.8 1
execute if score @s ln_kit matches 1 run data modify entity @e[tag=lb_kit3,limit=1] text set value '{"text": "醫療套件", "color": "#8EE07A", "font": "lnai:ui"}'
execute if score @s ln_kit matches 1 run title @s actionbar {"text": "醫療套件：急救包 +2、繃帶 +4，救隊友快一倍", "color": "#8EE07A", "font": "lnai:ui"}
execute if score @s ln_kit matches 2 run data modify entity @e[tag=lb_kit3,limit=1] text set value '{"text": "爆破套件", "color": "#F0A040", "font": "lnai:ui"}'
execute if score @s ln_kit matches 2 run title @s actionbar {"text": "爆破套件：C4 ×2、闊刀地雷 ×2、M67 +2", "color": "#F0A040", "font": "lnai:ui"}
execute if score @s ln_kit matches 3 run data modify entity @e[tag=lb_kit3,limit=1] text set value '{"text": "偵察套件", "color": "#7FC8E8", "font": "lnai:ui"}'
execute if score @s ln_kit matches 3 run title @s actionbar {"text": "偵察套件：偵察無人機＋遙控螢幕、煙霧彈 +2", "color": "#7FC8E8", "font": "lnai:ui"}
