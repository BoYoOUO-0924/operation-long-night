# 由 tools/build_ch01.py 自動產生，請勿手動修改
execute if score #t ln matches 20 run tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "▶ 目標：", "color": "yellow", "bold": true}, {"text": "往紅外線信標的方向降落到沙灘。", "color": "white"}]}
execute if score #t ln matches 20 run lnhud objective @a 往紅外線信標的方向降落到沙灘。
execute if score #t ln matches 20 run execute as @a at @s run playsound lnai:sfx.objective master @s ~ ~ ~ 0.8 1
execute if score #t ln matches 60 run lnhud say @a E0B050 150 "戰車" 我先說, 誰落地姿勢最醜, 回去請喝一整晚。
execute if score #t ln matches 140 run lnhud say @a 7FC8D8 160 "白鴉" 先擔心你自己別掛在崖上。信標在沙灘, 對準綠光。
execute if score #t ln matches 220 run lnhud say @a 8CC08C 105 "狐狸" 風往北吹, 往南邊偏一點。
execute if score #t ln matches 260 run tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "（提示）", "color": "gray"}, {"text": "看著羅盤上的綠點往那個方向移動；避開探照燈的光束。", "color": "gray", "italic": true}]}
execute if score #t ln matches 380 run lnhud say @a E0B050 120 "戰車" 哇喔——這個高度看海景還不錯嘛!
