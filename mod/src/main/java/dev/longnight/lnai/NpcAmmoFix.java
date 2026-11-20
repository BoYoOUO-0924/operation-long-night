package dev.longnight.lnai;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.Map;
import java.util.WeakHashMap;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * 修正：ZeroContact（防具模組）把 TaCZ 的「換彈要不要消耗彈藥」一律改成「要」，
 * 但 TaCZ NPC 身上沒有彈藥物品，換彈結束後彈匣還是 0 → NPC 不停換彈、一槍都不開。
 * 這裡在 NPC 換彈「裝填」階段結束的那一刻，直接把彈匣補滿（NPC 本來就是無限彈藥設計）。
 */
@Mod.EventBusSubscriber(modid = LnAi.MODID)
public final class NpcAmmoFix {
    private NpcAmmoFix() {}

    private static final Map<LivingEntity, String> LAST = new WeakHashMap<>();
    private static Class<?> npcClass;
    private static Method getHolder;
    private static Field stateField;
    private static boolean broken;

    @SubscribeEvent
    public static void tick(LivingEvent.LivingTickEvent e) {
        LivingEntity m = e.getEntity();
        if (broken || m.level().isClientSide) return;
        try {
            if (npcClass == null) npcClass = Class.forName("mod.cdv.tnpc.entity.AutoGunOperator");
            if (!npcClass.isInstance(m)) return;
            if (getHolder == null) getHolder = npcClass.getMethod("getDataHolder");
            Object h = getHolder.invoke(m);
            if (stateField == null) { stateField = h.getClass().getDeclaredField("reloadStateType"); stateField.setAccessible(true); }
            String now = String.valueOf(stateField.get(h));
            String prev = LAST.put(m, now);
            if (prev != null && prev.endsWith("_FEEDING") && !prev.equals(now)) refill(m.getMainHandItem());
        } catch (Throwable t) {
            broken = true;
            com.mojang.logging.LogUtils.getLogger().warn("[lnai] NpcAmmoFix disabled: {}", t.toString());
        }
    }

    private static void refill(ItemStack gun) throws Exception {
        CompoundTag tag = gun.getTag();
        if (tag == null || !tag.contains("GunId")) return;
        int cap = capacity(new ResourceLocation(tag.getString("GunId")));
        if (cap > 0 && tag.getInt("GunCurrentAmmoCount") < cap) tag.putInt("GunCurrentAmmoCount", cap);
    }

    private static Method getIndex, getGunData, getAmmoAmount;

    private static int capacity(ResourceLocation id) throws Exception {
        if (getIndex == null) {
            getIndex = Class.forName("com.tacz.guns.api.TimelessAPI").getMethod("getCommonGunIndex", ResourceLocation.class);
            getGunData = Class.forName("com.tacz.guns.resource.index.CommonGunIndex").getMethod("getGunData");
            getAmmoAmount = Class.forName("com.tacz.guns.resource.pojo.data.gun.GunData").getMethod("getAmmoAmount");
        }
        java.util.Optional<?> idx = (java.util.Optional<?>) getIndex.invoke(null, id);
        if (idx.isEmpty()) return 30;
        return (int) getAmmoAmount.invoke(getGunData.invoke(idx.get()));
    }
}
