package dev.longnight.lnai.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import dev.longnight.lnai.LnAi;
import java.lang.reflect.Field;
import java.util.HashMap;
import java.util.Map;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderLivingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * 隊友 NPC 腰側掛一把近戰武器（純裝飾，NPC 不會拿來用）。
 * TaCZ NPC 是用一個「假玩家」畫出來的（mod.cdv.tnpc.client.FakePlayer，欄位 link 指回 NPC），
 * 所以在假玩家畫完後，照它身體的姿勢把武器畫在右腰。
 */
@Mod.EventBusSubscriber(modid = LnAi.MODID, value = Dist.CLIENT)
public final class NpcSidearm {
    private NpcSidearm() {}

    /** 名字 → 腰上的武器 */
    private static final Map<String, String> BY_NAME = Map.of(
            "白鴉", "superbwarfare:military_shovel",
            "戰車", "superbwarfare:crowbar",
            "狐狸", "superbwarfare:knife");
    private static final Map<String, ItemStack> STACKS = new HashMap<>();
    private static Field link;
    private static boolean missing;
    /** 掛法（除錯指令 sidearm 可以即時調整）：位置 x y z（1/16 格）、旋轉 x y z（度）、大小、是否用手持視角 */
    static float px = -5.3f, py = 8.5f, pz = 0.5f, rx = -15, ry = 180, rz = 0, sc = 0.7f;
    static boolean hand = true;   // 用手持視角：每把武器的模型本來就有設定拿在手上的樣子，往下轉就像掛在腰上

    @SubscribeEvent
    public static void onRender(RenderLivingEvent.Post<?, ?> e) {
        LivingEntity fake = e.getEntity();
        if (missing || !fake.getClass().getName().equals("mod.cdv.tnpc.client.FakePlayer")) return;
        Entity npc = npcOf(fake);
        if (npc == null || !npc.hasCustomName()) return;
        String id = BY_NAME.get(npc.getCustomName().getString());
        if (id == null || !(e.getRenderer().getModel() instanceof HumanoidModel<?> model)) return;
        ItemStack stack = STACKS.computeIfAbsent(id, k -> new ItemStack(ForgeRegistries.ITEMS.getValue(new ResourceLocation(k))));
        if (stack.isEmpty()) return;

        PoseStack ps = e.getPoseStack();
        float pt = e.getPartialTick();
        ps.pushPose();
        // 跟 LivingEntityRenderer 一樣的轉換：轉到身體朝向 → 翻轉 → 移到模型原點
        ps.mulPose(Axis.YP.rotationDegrees(180f - Mth.rotLerp(pt, fake.yBodyRotO, fake.yBodyRot)));
        ps.scale(-1f, -1f, 1f);
        ps.translate(0, -1.501f, 0);
        model.body.translateAndRotate(ps);
        // 右腰外側（模型單位 1/16 格），武器朝下、略往後傾
        ps.translate(px / 16f, py / 16f, pz / 16f);
        ps.mulPose(Axis.XP.rotationDegrees(rx));
        ps.mulPose(Axis.YP.rotationDegrees(ry));
        ps.mulPose(Axis.ZP.rotationDegrees(rz));
        ps.scale(sc, sc, sc);
        Minecraft.getInstance().getItemRenderer().renderStatic(stack, hand ? ItemDisplayContext.THIRD_PERSON_RIGHT_HAND : ItemDisplayContext.FIXED, e.getPackedLight(),
                OverlayTexture.NO_OVERLAY, ps, e.getMultiBufferSource(), fake.level(), fake.getId());
        ps.popPose();
    }

    private static Entity npcOf(LivingEntity fake) {
        try {
            if (link == null) link = fake.getClass().getField("link");
            return (Entity) link.get(fake);
        } catch (Throwable t) {
            missing = true;
            return null;
        }
    }
}
