# 由 tools/build_ch01.py 自動產生，請勿手動修改
execute if score #t ln matches 20 run lnhud say @a 5BA8B0 150 "海神" 所有雷達離線。艦隊開火——獵犬, 離開砲台!
execute if score #t ln matches 120 run tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "▶ 目標：", "color": "yellow", "bold": true}, {"text": "撤到北邊的懸崖觀測站。", "color": "white"}]}
execute if score #t ln matches 120 run lnhud objective @a 撤到北邊的懸崖觀測站。
execute if score #t ln matches 120 run execute as @a at @s run playsound lnai:sfx.objective master @s ~ ~ ~ 0.8 1
execute if score #t ln matches 180 run lnhud say @a E0B050 70 "戰車" 這才叫煙火!
execute if score #t ln matches 400 run lnhud say @a 8CC08C 180 "狐狸" 等等……這能量讀數不對。是從山體裡面來的, 而且在升高。
execute if score #t ln matches 540 run lnhud say @a 7FC8D8 130 "白鴉" 海神, 聽得到嗎? 山裡面有東西——
execute if score #t ln matches 620 run lnhud say @a 5BA8B0 150 "海神" （劇烈雜訊）……訊號遭強電磁干擾……獵犬……
execute if score #t ln matches 740 run lnhud say @a D05050 135 "守夜人" 雷達? 你們以為我需要那種過時的玩具?
execute if score #t ln matches 860 run lnhud say @a D05050 200 "守夜人" 歡迎來到黑石海岸, 獵犬小隊。謝謝你們替我把艦隊……請進了射程。
execute if score #t ln matches 1020 run lnhud say @a D05050 85 "守夜人" 祝你們好夢。晚安。
execute if score #t ln matches 1120 run lnhud say @a E0B050 135 "戰車" 這傢伙是誰? 他怎麼會在我們的頻道上?
execute if score #t ln matches 1220 run lnhud say @a 8CC08C 150 "狐狸" 不知道。但頻道全被蓋台了, 連艦隊都叫不到。
execute if score #t ln matches 1320 run lnhud say @a 7FC8D8 170 "白鴉" 上北邊的懸崖觀測站, 用那裡的有線線路警告艦隊。快!
