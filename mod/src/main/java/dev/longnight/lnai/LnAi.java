package dev.longnight.lnai;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * 長夜：小隊 AI ＋ 戰術介面。
 *
 * 伺服器端：NPC 小隊 AI（ForgeData 下命令）、友軍不互傷、擊殺通報、醫療／投擲物固定欄位、/lnhud 指令。
 * 玩家端（client 套件）：介面（血量、護甲、隊友、目標、物品欄）、5 醫療／4 投擲的短按長按輪盤、投擲拋物線、字型。
 *
 * NPC 命令（ForgeData）：
 *   ln_side "red"/"blue"、ln_squad、ln_wp [I;x,y,z]、ln_wpr、ln_speed、ln_hunt、ln_follow 1b、ln_slot
 */
@Mod(LnAi.MODID)
public class LnAi {
    public static final String MODID = "lnai";
    public static final ResourceLocation FONT = new ResourceLocation(MODID, "ui");
    private static final ResourceLocation TACZ_NPC = new ResourceLocation("tacznpcs", "npc");

    public LnAi() {
        IEventBus mod = FMLJavaModLoadingContext.get().getModEventBus();
        ModItems.ITEMS.register(mod);
        mod.addListener((FMLCommonSetupEvent e) -> e.enqueueWork(Net::register));

        MinecraftForge.EVENT_BUS.addListener(this::onJoin);
        MinecraftForge.EVENT_BUS.addListener(CombatEvents::onAttack);
        MinecraftForge.EVENT_BUS.addListener(CombatEvents::onDeath);
        MinecraftForge.EVENT_BUS.addListener(Heal::onTick);
        MinecraftForge.EVENT_BUS.addListener(HudCommand::register);
        MinecraftForge.EVENT_BUS.addListener(HudCommand::onServerTick);
        MinecraftForge.EVENT_BUS.addListener(Cutscenes::onReload);
        MinecraftForge.EVENT_BUS.addListener(Cutscenes::onTick);
        MinecraftForge.EVENT_BUS.addListener((PlayerEvent.PlayerLoggedInEvent e) -> {
            if (e.getEntity() instanceof ServerPlayer p) HudCommand.resend(p);
        });
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
