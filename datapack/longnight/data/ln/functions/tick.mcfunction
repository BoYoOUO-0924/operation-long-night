# 依目前章節（#run ln：1 = 第一章，其他 = 第五章）分派每 tick 的關卡邏輯
execute if score #run ln matches 1 if score #stage ln matches 1.. run function ln:ch01/tick
execute unless score #run ln matches 1 if score #stage ln matches 1.. run function ln:ch05/tick
