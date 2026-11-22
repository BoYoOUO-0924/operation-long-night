# 由 tools/build_ch01.py 自動產生，請勿手動修改
execute if score #t ln matches 20 run lnhud say @a 5BA8B0 165 "海神" 獵犬小隊, 這裡是海神。你們已經進入黑石海岸上空。
execute if score #t ln matches 100 run lnhud say @a 5BA8B0 155 "海神" 艦隊正在接近。那三座雷達不倒, 我們就是瞎子。
execute if score #t ln matches 180 run lnhud say @a 8CC08C 180 "狐狸" 三座雷達都標進你們的目鏡了: 北崖、砲台中央、燈塔頂上。
execute if score #t ln matches 260 run tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "▶ 目標：", "color": "yellow", "bold": true}, {"text": "往紅外線信標的方向降落到沙灘。", "color": "white"}]}
execute if score #t ln matches 260 run lnhud objective @a 往紅外線信標的方向降落到沙灘。
execute if score #t ln matches 260 run execute as @a at @s run playsound lnai:sfx.objective master @s ~ ~ ~ 0.8 1
execute if score #t ln matches 300 run lnhud say @a E0B050 150 "戰車" 我先說, 誰落地姿勢最醜, 回去請喝一整晚。
execute if score #t ln matches 380 run lnhud say @a 7FC8D8 160 "白鴉" 先擔心你自己別掛在崖上。信標在沙灘, 對準綠光。
execute if score #t ln matches 460 run lnhud say @a 8CC08C 175 "狐狸" 那是紅外線信標, 只有我們的目鏡看得到, 敵人看不到。
execute if score #t ln matches 540 run lnhud say @a 7FC8D8 145 "白鴉" 探照燈在掃。別讓光照到你, 會引來高射砲。
execute if score #t ln matches 600 run lnhud say @a 8CC08C 105 "狐狸" 風往北吹, 往南邊偏一點。
execute if score #t ln matches 660 run lnhud say @a E0B050 120 "戰車" 哇喔——這個高度看海景還不錯嘛!
execute if score #t ln matches 620 run tellraw @a {"text": "", "font": "lnai:ui", "extra": [{"text": "（提示）", "color": "gray"}, {"text": "看著羅盤上的綠點往那個方向移動；避開探照燈的光束。", "color": "gray", "italic": true}]}
