# 由 tools/build_ch01.py 自動產生，請勿手動修改
execute if score #t ln matches 220 run tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "▶ 目標：", "color": "yellow", "bold": true}, {"text": "爬上海崖, 破壞探照燈和防空砲。", "color": "white"}]}
execute if score #t ln matches 220 run lnhud objective @a 爬上海崖, 破壞探照燈和防空砲。
execute if score #t ln matches 220 run execute as @a at @s run playsound lnai:sfx.objective master @s ~ ~ ~ 0.8 1
execute if score #t ln matches 280 run lnhud say @a 7FC8D8 115 "白鴉" 我找個高點掩護你們, 往上走。
execute if score #t ln matches 380 run lnhud say @a E0B050 160 "戰車" 上面那門防空砲還在打我們的運輸機, 先把它拆了。
execute if score #t ln matches 1400 run tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "（提示）", "color": "gray"}, {"text": "沙灘北邊有一條沿著崖壁往上的小路。", "color": "gray", "italic": true}]}
