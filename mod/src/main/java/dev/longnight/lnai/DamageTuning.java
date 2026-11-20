package dev.longnight.lnai;

import java.lang.reflect.Method;
import java.util.Map;
import java.util.WeakHashMap;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.entity.living.LivingDamageEvent;
import net.minecraftforge.eventbus.api.Event;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * 敵人的子彈傷害（第五章起）：
 * 敵人穿的 ZeroContact 防彈衣等級很高，原本打軀幹每發只剩 0.02 傷害，幾乎打不死。
 * 改成：子彈打到敵人（紅方）時，最終傷害 = 槍的基礎傷害（已含距離衰減）× ENEMY_FACTOR，爆頭再 × HEAD_MULT。
 * M4A1：25 格內 6.5 → 每發 4.2，軀幹 5 發擊殺；25～60 格 6 發；爆頭 2 發。
 * 玩家與友軍受到的傷害不變（仍由 ZeroContact 防具計算）。
 * /lnhud dmgdebug true：在伺服器紀錄每一發的傷害。
 */
@Mod.EventBusSubscriber(modid = LnAi.MODID)
public final class DamageTuning {
    private DamageTuning() {}

    static final float ENEMY_FACTOR = 0.65f;
    static final float HEAD_MULT = 3.0f;
    static boolean debug = false;

    private record Hit(Entity bullet, float base, boolean head, boolean[] used) {}
    private static final Map<LivingEntity, Hit> HITS = new WeakHashMap<>();
    private static Method mHurt, mBullet, mBase, mHead;

    /** TaCZ 是選用相依：用反射掛它的命中事件，沒有 TaCZ 也不會出錯 */
    @SuppressWarnings("unchecked")
    static void init() {
        try {
            Class<? extends Event> pre = (Class<? extends Event>) Class.forName("com.tacz.guns.api.event.common.EntityHurtByGunEvent$Pre");
            mHurt = pre.getMethod("getHurtEntity");
            mBullet = pre.getMethod("getBullet");
            mBase = pre.getMethod("getBaseAmount");
            mHead = pre.getMethod("isHeadShot");
            MinecraftForge.EVENT_BUS.addListener(EventPriority.HIGHEST, false, (Class<Event>) pre, DamageTuning::onGunHit);   // 最先讀：ZeroContact 會在後面改掉基礎傷害
        } catch (Throwable t) {
            com.mojang.logging.LogUtils.getLogger().warn("[lnai] DamageTuning: TaCZ hit event unavailable: {}", t.toString());
        }
    }

    private static void onGunHit(Event e) {
        try {
            if (!(mHurt.invoke(e) instanceof LivingEntity t) || t.level().isClientSide) return;
            if (!"red".equals(Orders.side(t))) return;
            HITS.put(t, new Hit((Entity) mBullet.invoke(e), (float) mBase.invoke(e), (boolean) mHead.invoke(e), new boolean[1]));
        } catch (Throwable ignored) {
        }
    }

    /** 防具把傷害完全擋掉（0）時 Forge 不會走到最終傷害，這裡留一點讓下面的覆寫能執行 */
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void hurt(net.minecraftforge.event.entity.living.LivingHurtEvent e) {
        Hit h = HITS.get(e.getEntity());
        if (h != null && !h.used()[0] && e.getSource().getDirectEntity() == h.bullet() && e.getAmount() <= 0) e.setAmount(0.01f);
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void damage(LivingDamageEvent e) {
        LivingEntity t = e.getEntity();
        Entity direct = e.getSource().getDirectEntity();
        Hit h = HITS.get(t);
        if (h == null || direct != h.bullet()) return;
        float before = e.getAmount();
        if (h.used()[0]) {
            e.setAmount(0);   // 同一發子彈被防具拆成好幾段傷害：只算第一段
        } else {
            h.used()[0] = true;
            e.setAmount(h.base() * ENEMY_FACTOR * (h.head() ? HEAD_MULT : 1));
        }
        if (debug) {
            Entity by = e.getSource().getEntity();
            com.mojang.logging.LogUtils.getLogger().info("[lnai] dmg {} <- {} base {} head {} armor-calc {} -> {} hp {}/{}",
                    t.getName().getString(), by == null ? "?" : by.getName().getString(), h.base(), h.head(),
                    before, e.getAmount(), t.getHealth(), t.getMaxHealth());
        }
    }
}
