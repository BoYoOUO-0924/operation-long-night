# 由 tools/build_lobby.py 自動產生，請勿手動修改
function ln:lobby/chap_ok
execute if score #ok ln matches 0 on target run tellraw @s {"text": "這一章還在製作中，請先選「可出擊」的章節。", "color": "#F0A040", "font": "lnai:ui"}
execute if score #ok ln matches 1 run function ln:lobby/toggle_ready
