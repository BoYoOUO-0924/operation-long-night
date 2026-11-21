# 由 tools/build_lobby.py 自動產生，請勿手動修改
execute unless score #ct ln matches 0.. run scoreboard players set #ct ln 0
execute if score #ccd ln matches 1.. run scoreboard players remove #ccd ln 1
execute if score #ct ln matches 0 unless score #ccd ln matches 1.. positioned -296.5 273 931 if entity @a[gamemode=adventure,distance=..6] run function ln:lobby/chat_start
execute if score #ct ln matches 1.. run scoreboard players add #ct ln 1
execute if score #cv ln matches 1 if score #ct ln matches 2 positioned -296.5 273 931 run lnhud say @a[distance=..16] E0B050 175 "戰車" 這批彈鏈誰裝的? 三發就卡一次, 回去我要找後勤算帳。
execute if score #cv ln matches 1 if score #ct ln matches 162 positioned -296.5 273 931 run lnhud say @a[distance=..16] 8CC08C 130 "狐狸" 你上次也這樣說, 結果回去就睡死了。
execute if score #cv ln matches 1 if score #ct ln matches 277 positioned -296.5 273 931 run lnhud say @a[distance=..16] E0B050 75 "戰車" ……那次不算。
execute if score #cv ln matches 1 if score #ct ln matches 367.. run function ln:lobby/chat_end
execute if score #cv ln matches 2 if score #ct ln matches 2 positioned -296.5 273 931 run lnhud say @a[distance=..16] 8CC08C 135 "狐狸" 白鴉, 你那片鏡子再擦下去都要擦穿了。
execute if score #cv ln matches 2 if score #ct ln matches 122 positioned -296.5 273 931 run lnhud say @a[distance=..16] 7FC8D8 110 "白鴉" 起霧一次, 就少一個人回家。
execute if score #cv ln matches 2 if score #ct ln matches 217 positioned -296.5 273 931 run lnhud say @a[distance=..16] 8CC08C 90 "狐狸" ……好啦, 你繼續。
execute if score #cv ln matches 2 if score #ct ln matches 322.. run function ln:lobby/chat_end
execute if score #cv ln matches 3 if score #ct ln matches 2 positioned -296.5 273 931 run lnhud say @a[distance=..16] 8CC08C 160 "狐狸" 腕部終端校準好了, 等一下你們的位置我都看得到。
execute if score #cv ln matches 3 if score #ct ln matches 147 positioned -296.5 273 931 run lnhud say @a[distance=..16] E0B050 100 "戰車" 所以我上廁所你也看得到?
execute if score #cv ln matches 3 if score #ct ln matches 232 positioned -296.5 273 931 run lnhud say @a[distance=..16] 8CC08C 100 "狐狸" 看得到, 而且我會截圖。
execute if score #cv ln matches 3 if score #ct ln matches 347.. run function ln:lobby/chat_end
execute if score #cv ln matches 4 if score #ct ln matches 2 positioned -296.5 273 931 run lnhud say @a[distance=..16] E0B050 145 "戰車" 隊長, 等一下落地你先走, 我在後面顧你。
execute if score #cv ln matches 4 if score #ct ln matches 132 positioned -296.5 273 931 run lnhud say @a[distance=..16] 7FC8D8 115 "白鴉" 你看得到的地方, 我都看得到。
execute if score #cv ln matches 4 if score #ct ln matches 232 positioned -296.5 273 931 run lnhud say @a[distance=..16] 8CC08C 120 "狐狸" 通訊斷了就照備案走, 別逞強喔。
execute if score #cv ln matches 4 if score #ct ln matches 367.. run function ln:lobby/chat_end
execute if score #cv ln matches 5 if score #ct ln matches 2 positioned -296.5 273 931 run lnhud say @a[distance=..16] 8CC08C 140 "狐狸" 高度一萬米, 外面零下五十度。誰要先跳?
execute if score #cv ln matches 5 if score #ct ln matches 127 positioned -296.5 273 931 run lnhud say @a[distance=..16] E0B050 115 "戰車" 誰最重誰先, 傘才不會被壓到。
execute if score #cv ln matches 5 if score #ct ln matches 227 positioned -296.5 273 931 run lnhud say @a[distance=..16] 8CC08C 70 "狐狸" 那就是你啊。
execute if score #cv ln matches 5 if score #ct ln matches 282 positioned -296.5 273 931 run lnhud say @a[distance=..16] 7FC8D8 70 "白鴉" 我同意。
execute if score #cv ln matches 5 if score #ct ln matches 362.. run function ln:lobby/chat_end
execute if score #cv ln matches 6 if score #ct ln matches 2 positioned -296.5 273 931 run lnhud say @a[distance=..16] E0B050 115 "戰車" 這趟打完, 我要吃三碗牛肉麵。
execute if score #cv ln matches 6 if score #ct ln matches 102 positioned -296.5 273 931 run lnhud say @a[distance=..16] 8CC08C 75 "狐狸" 你上次說兩碗。
execute if score #cv ln matches 6 if score #ct ln matches 162 positioned -296.5 273 931 run lnhud say @a[distance=..16] E0B050 75 "戰車" 上次比較輕鬆。
execute if score #cv ln matches 6 if score #ct ln matches 222 positioned -296.5 273 931 run lnhud say @a[distance=..16] 7FC8D8 90 "白鴉" 我請。活著回來的話。
execute if score #cv ln matches 6 if score #ct ln matches 327.. run function ln:lobby/chat_end
