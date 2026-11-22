# 由 tools/build_ch01.py 自動產生，請勿手動修改
tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "▶ 目標：", "color": "yellow", "bold": true}, {"text": "掩護狐狸破解大門電子鎖。", "color": "white"}]}
lnhud objective @a 掩護狐狸破解大門電子鎖。
execute as @a at @s run playsound lnai:sfx.objective master @s ~ ~ ~ 0.8 1
