package dev.longnight.lnai;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * 長夜小隊 AI：替 TACZ NPC 補上「聽命令移動、小隊共享目標、跟隨玩家、主動搜索」。
 *
 * 只在伺服器端運作，玩家不用安裝。所有命令都透過實體的 ForgeData 下達（資料包可以用 data modify 設定）：
 *   ln_side   "red" / "blue"        陣營（藍方 = 玩家方）
 *   ln_squad  字串                    小隊代號；同小隊會共享目標
 *   ln_wp     [I; x, y, z]           目標點：沒有交戰時往這裡移動
 *   ln_wpr    int                    到達半徑（預設 3）
 *   ln_speed  float                  移動速度倍率（預設 1.0）
 *   ln_hunt   int                    主動搜索半徑：在範圍內「知道」敵人在哪（不需要看見）
 *   ln_follow 1b                     跟隨最近的玩家（隊友用）
 *   ln_slot   int                    跟隨／隊形的位置編號（錯開站位）
 */
@Mod(LnAi.MODID)
public class LnAi {
    public static final String MODID = "lnai";
    private static final ResourceLocation TACZ_NPC = new ResourceLocation("tacznpcs", "npc");

    public LnAi() {
        MinecraftForge.EVENT_BUS.addListener(this::onJoin);
    }

    private void onJoin(EntityJoinLevelEvent event) {
        if (event.getLevel().isClientSide()) return;
        if (!(event.getEntity() instanceof PathfinderMob mob)) return;
        if (!TACZ_NPC.equals(ForgeRegistries.ENTITY_TYPES.getKey(mob.getType()))) return;
        AttributeInstance range = mob.getAttribute(Attributes.FOLLOW_RANGE);
        if (range != null && range.getBaseValue() < 64) range.setBaseValue(64);   // 尋路距離加長，才會繞遠路
        mob.goalSelector.addGoal(3, new ChaseGoal(mob));
        mob.goalSelector.addGoal(4, new OrderMoveGoal(mob));
        mob.goalSelector.addGoal(5, new FollowPlayerGoal(mob));
        mob.targetSelector.addGoal(6, new SquadTargetGoal(mob));
    }
}
