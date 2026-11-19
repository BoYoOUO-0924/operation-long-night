# 由 tools/build_level.py 自動產生，請勿手動修改
scoreboard players set #evgen ln 1
scoreboard players set #gent ln 0
setblock 112 145 982 lever[face=floor,facing=north,powered=false]
function ln:ch05/evdlg/generator_fail
scoreboard players set #route ln 2
function ln:ch05/dir/spawn_next
