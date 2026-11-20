# 由 tools/build_level.py 自動產生，請勿手動修改
scoreboard players set #evgen ln 1
scoreboard players set #gent ln 0
setblock 112 145 982 lever[face=floor,facing=north,powered=false]
kill @e[tag=ln_genhint]
setblock 112 146 982 light[level=13]
summon text_display 112.5 147 982.5 {Tags:["ln","ln_genhint"],billboard:"center",see_through:1b,transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[4f,4f,4f]},brightness:{sky:15,block:15},background:1711276032,text:'{"text": "⚡ 拉起拉桿 (右鍵)", "color": "#F0A040", "font": "lnai:ui"}'}
function ln:ch05/evdlg/generator_fail
scoreboard players set #route ln 2
function ln:ch05/dir/spawn_next
