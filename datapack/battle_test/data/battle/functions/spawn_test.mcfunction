summon tacznpcs:npc ~20 ~ ~-9 {template:"red_assault",PersistenceRequired:1b}
summon tacznpcs:npc ~20 ~ ~-7 {template:"red_assault",PersistenceRequired:1b}
summon tacznpcs:npc ~20 ~ ~-5 {template:"red_assault",PersistenceRequired:1b}
summon tacznpcs:npc ~20 ~ ~-3 {template:"red_assault",PersistenceRequired:1b}
summon tacznpcs:npc ~20 ~ ~-1 {template:"red_support",PersistenceRequired:1b}
summon tacznpcs:npc ~20 ~ ~1 {template:"red_support",PersistenceRequired:1b}
summon tacznpcs:npc ~20 ~ ~3 {template:"red_sniper",PersistenceRequired:1b}
summon tacznpcs:npc ~20 ~ ~5 {template:"red_sniper",PersistenceRequired:1b}
summon tacznpcs:npc ~20 ~ ~7 {template:"red_cqb",PersistenceRequired:1b}
summon tacznpcs:npc ~20 ~ ~9 {template:"red_cqb",PersistenceRequired:1b}
summon tacznpcs:npc ~-20 ~ ~-9 {template:"blue_assault",PersistenceRequired:1b}
summon tacznpcs:npc ~-20 ~ ~-7 {template:"blue_assault",PersistenceRequired:1b}
summon tacznpcs:npc ~-20 ~ ~-5 {template:"blue_assault",PersistenceRequired:1b}
summon tacznpcs:npc ~-20 ~ ~-3 {template:"blue_assault",PersistenceRequired:1b}
summon tacznpcs:npc ~-20 ~ ~-1 {template:"blue_support",PersistenceRequired:1b}
summon tacznpcs:npc ~-20 ~ ~1 {template:"blue_support",PersistenceRequired:1b}
summon tacznpcs:npc ~-20 ~ ~3 {template:"blue_sniper",PersistenceRequired:1b}
summon tacznpcs:npc ~-20 ~ ~5 {template:"blue_sniper",PersistenceRequired:1b}
summon tacznpcs:npc ~-20 ~ ~7 {template:"blue_cqb",PersistenceRequired:1b}
summon tacznpcs:npc ~-20 ~ ~9 {template:"blue_cqb",PersistenceRequired:1b}
tellraw @a {"text":"[大戰場測試] 已生成 10 對 10（西：藍隊 / 東：紅隊）","color":"green"}
function battle:count
