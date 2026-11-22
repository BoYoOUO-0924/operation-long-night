# 全隊覆沒時由 lnai 模組呼叫：交給目前進行中的章節處理
execute if score #run ln matches 1 if score #stage ln matches 1.. run function ln:ch01/wipe
execute unless score #run ln matches 1 if score #stage ln matches 1.. run function ln:ch05/wipe
