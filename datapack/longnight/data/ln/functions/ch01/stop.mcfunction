# 由 tools/build_ch01.py 自動產生，請勿手動修改
function ln:ch01/cleanup
gamemode creative @a
tellraw @a {"text": "[長夜] 已中止第一章。", "color": "red", "font": "lnai:ui"}
