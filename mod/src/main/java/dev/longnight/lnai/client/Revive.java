package dev.longnight.lnai.client;

import com.mojang.blaze3d.platform.InputConstants;
import dev.longnight.lnai.LnAi;
import dev.longnight.lnai.Net;
import java.lang.reflect.Method;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.lwjgl.glfw.GLFW;

/**
 * 客戶端的倒地與救援：
 * 自己倒地 → 強制 TaCZ 趴下、畫面邊緣變紅、顯示剩餘秒數與誰在救你；
 * 靠近倒地隊友 → 提示「按住 F 救援」，按住時送給伺服器，畫出 4 秒進度。
 */
@Mod.EventBusSubscriber(modid = LnAi.MODID, value = Dist.CLIENT)
public final class Revive {
    private Revive() {}

    public static final KeyMapping KEY = new KeyMapping("key.lnai.revive", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_F, "key.categories.lnai");
    static final double RANGE = 2.5;

    private static boolean downed = false;
    private static int target = -1;      // 正在救的人（實體編號）
    private static int held = 0;         // 已經按住幾 tick（畫進度用）
    private static int crawlCheck = 0;

    public static void onDowned(boolean down) {
        downed = down;
        crawl(down);
    }

    public static boolean downed() { return downed; }

    // ---- TaCZ 趴下（反射呼叫，不直接依賴 TaCZ） ----
    private static Method fromLocal, crawlM, isCrawlM;

    private static void crawl(boolean on) {
        LocalPlayer p = Minecraft.getInstance().player;
        if (p == null) return;
        try {
            if (fromLocal == null) {
                Class<?> c = Class.forName("com.tacz.guns.api.client.gameplay.IClientPlayerGunOperator");
                fromLocal = c.getMethod("fromLocalPlayer", LocalPlayer.class);
                crawlM = c.getMethod("crawl", boolean.class);
                isCrawlM = c.getMethod("isCrawl");
            }
            Object op = fromLocal.invoke(null, p);
            if ((boolean) isCrawlM.invoke(op) != on) crawlM.invoke(op, on);
        } catch (Throwable ignored) {}
    }

    @SubscribeEvent
    public static void tick(TickEvent.ClientTickEvent e) {
        if (e.phase != TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer p = mc.player;
        if (p == null) { downed = false; target = -1; return; }
        if (downed) {
            if (++crawlCheck % 10 == 0) crawl(true);   // 玩家按 Z 想站起來也會被趴回去
            p.setSprinting(false);
            release();
            return;
        }
        Net.Mate t = KEY.isDown() && mc.screen == null ? nearestDowned(p) : null;
        if (t == null) { release(); return; }
        if (t.entity() != target) {
            release();
            target = t.entity();
            held = 0;
            Net.CH.sendToServer(new Net.Revive(target, true));
        }
        held++;
        // 救人時不能開槍
        while (mc.options.keyAttack.consumeClick()) {}
    }

    private static void release() {
        if (target != -1) Net.CH.sendToServer(new Net.Revive(target, false));
        target = -1;
        held = 0;
    }

    static Net.Mate nearestDowned(LocalPlayer p) {
        Net.Mate best = null;
        double bd = RANGE;
        for (Net.Mate m : Hud.mates(p)) {
            if (!m.downed()) continue;
            Entity en = Minecraft.getInstance().level.getEntity(m.entity());
            if (en == null) continue;
            double d = en.distanceTo(p);
            if (d <= bd) { bd = d; best = m; }
        }
        return best;
    }

    /** 畫面中央：自己倒地的狀態、或救援提示與進度 */
    static void draw(GuiGraphics g, int w, int h, float pt) {
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer p = mc.player;
        if (p == null || CutscenePlayer.active()) return;
        long now = ClientState.now();
        if (downed) {
            Net.Mate me = Hud.self(p);
            float pulse = 0.55f + 0.2f * (float) Math.sin((now + pt) * 0.25);
            int edge = Math.round(pulse * 0xB0) << 24 | 0x5A0A08;
            g.fillGradient(0, 0, w, h / 3, edge, 0x005A0A08);
            g.fillGradient(0, h * 2 / 3, w, h, 0x005A0A08, edge);
            int cy = h / 2 + 30;
            Hud.scaled(g, "倒地", w / 2 - Math.round(Hud.width("倒地") * 1.8f / 2), cy - 6, 0xFFE4E2DA, 1.8f, false);
            String line;
            float bar;
            int col;
            if (me != null && me.revive() > 0 && !me.helper().isEmpty()) {
                line = me.helper() + " 正在救你";
                bar = me.revive();
                col = 0xFF9DB497;
            } else {
                int sec = me == null ? 0 : me.bleedSec();
                line = (me != null && !me.helper().isEmpty() ? me.helper() + " 正在趕來　" : "等待救援　") + sec + " 秒";
                bar = me == null ? 1 : me.bleed();
                col = 0xFFFF8A78;
            }
            Hud.text(g, line, w / 2, cy + 18, 0xFFE4E2DA, true);
            Hud.bar(g, w / 2 - 60, cy + 30, 120, 2, bar, col);
            Hud.small(g, "只能用手槍，可以慢慢爬到掩體後面", w / 2, cy + 38, 0xFFA4ACB4, true);
            return;
        }
        if (target != -1) {
            Net.Mate t = null;
            for (Net.Mate m : Hud.mates(p)) if (m.entity() == target) t = m;
            String n = t == null ? "" : t.name();
            Hud.text(g, "救援 " + n, w / 2, h / 2 + 22, 0xFFE4E2DA, true);
            Hud.bar(g, w / 2 - 50, h / 2 + 34, 100, 2, held / 80f, 0xFF9DB497);
            return;
        }
        Net.Mate t = nearestDowned(p);
        if (t != null) {
            String keyName = KEY.getTranslatedKeyMessage().getString().toUpperCase();
            Hud.text(g, "按住 " + keyName + " 救援 " + t.name(), w / 2, h / 2 + 22, 0xFFE4E2DA, true);
        }
    }
}
