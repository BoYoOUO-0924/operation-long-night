package dev.longnight.lnai.client;

import java.util.ArrayList;
import java.util.List;
import dev.longnight.lnai.Gear;
import dev.longnight.lnai.LnAi;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.CustomizeGuiOverlayEvent;
import net.minecraftforge.client.event.RegisterGuiOverlaysEvent;
import net.minecraftforge.client.event.RenderGuiOverlayEvent;
import net.minecraftforge.client.gui.overlay.VanillaGuiOverlay;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** 戰術介面：取代原版的愛心、盔甲、飢餓、經驗條、快捷欄與王條。 */
public final class Hud {
    private Hud() {}

    static final int PANEL = 0x99141A22, DIM = 0x33FFFFFF, WHITE = 0xFFFFFFFF, GRAY = 0xFFC8C8C8,
            AMBER = 0xFFFAC775, TEAL = 0xFF5DCAA5, ORANGE = 0xFFEF9F27, RED = 0xFFE24B4A, PINK = 0xFFF09595, BLUE = 0xFF85B7EB;
    static final String[] SQUAD = {"白鴉", "戰車", "狐狸"};

    // ---------- 字型與繪圖小工具 ----------
    static MutableComponent t(String s) { return Component.literal(s).withStyle(st -> st.withFont(LnAi.FONT)); }

    static int width(String s) { return Minecraft.getInstance().font.width(t(s)); }

    /** 畫字；centered = 以 x 為中心。 */
    static void text(GuiGraphics g, String s, int x, int y, int color, boolean centered) {
        Font f = Minecraft.getInstance().font;
        MutableComponent c = t(s);
        g.drawString(f, c, centered ? x - f.width(c) / 2 : x, y, color, true);
    }

    static void right(GuiGraphics g, String s, int x, int y, int color) { text(g, s, x - width(s), y, color, false); }

    static void big(GuiGraphics g, String s, int x, int y, int color, float scale) {
        g.pose().pushPose();
        g.pose().translate(x, y, 0);
        g.pose().scale(scale, scale, 1);
        g.drawString(Minecraft.getInstance().font, t(s), 0, 0, color, true);
        g.pose().popPose();
    }

    static void bar(GuiGraphics g, int x, int y, int w, int h, float v, int color) {
        g.fill(x, y, x + w, y + h, DIM);
        g.fill(x, y, x + Math.round(w * Math.max(0, Math.min(1, v))), y + h, color);
    }

    static void box(GuiGraphics g, int x, int y, int w, int h, int color) {
        g.fill(x, y, x + w, y + 1, color);
        g.fill(x, y + h - 1, x + w, y + h, color);
        g.fill(x, y, x + 1, y + h, color);
        g.fill(x + w - 1, y, x + w, y + h, color);
    }

    static boolean active() { return ClientInput.active(Minecraft.getInstance().player); }

    // ---------- 註冊與隱藏原版 ----------
    @Mod.EventBusSubscriber(modid = LnAi.MODID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.MOD)
    public static final class Setup {
        @SubscribeEvent
        public static void overlays(RegisterGuiOverlaysEvent e) {
            e.registerAboveAll("ln_hud", (gui, g, pt, w, h) -> { if (active()) draw(g, w, h); });
        }
    }

    @Mod.EventBusSubscriber(modid = LnAi.MODID, value = Dist.CLIENT)
    public static final class Hide {
        @SubscribeEvent
        public static void pre(RenderGuiOverlayEvent.Pre e) {
            if (!active()) return;
            var id = e.getOverlay().id();
            if (id.equals(VanillaGuiOverlay.HOTBAR.id()) || id.equals(VanillaGuiOverlay.PLAYER_HEALTH.id())
                    || id.equals(VanillaGuiOverlay.ARMOR_LEVEL.id()) || id.equals(VanillaGuiOverlay.FOOD_LEVEL.id())
                    || id.equals(VanillaGuiOverlay.EXPERIENCE_BAR.id()) || id.equals(VanillaGuiOverlay.ITEM_NAME.id()))
                e.setCanceled(true);
        }

        /** 王條（敵軍剩餘兵力）換成細條＋自己的字。 */
        @SubscribeEvent
        public static void boss(CustomizeGuiOverlayEvent.BossEventProgress e) {
            if (!active()) return;
            e.setCanceled(true);
            GuiGraphics g = e.getGuiGraphics();
            int cx = e.getWindow().getGuiScaledWidth() / 2, y = e.getY() + 2;
            Component name = e.getBossEvent().getName().copy().withStyle(st -> st.withFont(LnAi.FONT));
            Font f = Minecraft.getInstance().font;
            g.drawString(f, name, cx - f.width(name) / 2, y, WHITE, true);
            bar(g, cx - 90, y + 11, 180, 3, e.getBossEvent().getProgress(), RED);
            e.setIncrement(20);
        }
    }

    // ---------- 主畫面 ----------
    static void draw(GuiGraphics g, int w, int h) {
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer p = mc.player;
        long now = ClientState.now();
        objective(g, p);
        squad(g, p, now);
        feed(g, w, h, now);
        center(g, w, h, now);
        health(g, p, h);
        slots(g, p, w, h);
    }

    static void objective(GuiGraphics g, LocalPlayer p) {
        if (ClientState.objective.isEmpty()) return;
        int x = 8, y = 8;
        text(g, "目標", x, y, AMBER, false);
        y += 11;
        for (var line : Minecraft.getInstance().font.split(t(ClientState.objective), 150)) {
            g.drawString(Minecraft.getInstance().font, line, x, y, WHITE, true);
            y += 10;
        }
        if (ClientState.waypoint != null)
            text(g, "距離 " + Math.round(Math.sqrt(p.distanceToSqr(ClientState.waypoint))) + "m", x, y, GRAY, false);
    }

    private static final List<LivingEntity> squadCache = new ArrayList<>();
    private static long squadAt = -100;

    static LivingEntity find(String name) {
        for (LivingEntity e : squadCache) if (e.isAlive() && e.hasCustomName() && e.getCustomName().getString().equals(name)) return e;
        return null;
    }

    static void squad(GuiGraphics g, LocalPlayer p, long now) {
        if (now - squadAt > 10 || now < squadAt) {
            squadAt = now;
            squadCache.clear();
            for (Entity e : Minecraft.getInstance().level.entitiesForRendering())
                if (e instanceof LivingEntity le && le != p && le.hasCustomName()) {
                    String n = le.getCustomName().getString();
                    for (String s : SQUAD) if (s.equals(n)) squadCache.add(le);
                }
        }
        if (squadCache.isEmpty()) return;
        int x = 8, y = 76, wdt = 92;
        g.fill(x - 4, y - 4, x + wdt + 4, y + 13 + SQUAD.length * 17, PANEL);
        text(g, "獵犬小隊", x, y, TEAL, false);
        y += 13;
        for (String s : SQUAD) {
            LivingEntity e = find(s);
            text(g, s, x, y, e == null ? 0xFF777777 : WHITE, false);
            if (e == null) { right(g, "—", x + wdt, y, GRAY); y += 17; continue; }
            right(g, Math.round(e.distanceTo(p)) + "m", x + wdt, y, GRAY);
            float v = e.getHealth() / e.getMaxHealth();
            bar(g, x, y + 10, wdt, 2, v, v > 0.6f ? TEAL : v > 0.3f ? ORANGE : RED);
            y += 17;
        }
    }

    static void feed(GuiGraphics g, int w, int h, long now) {
        int y = h * 2 / 5;
        ClientState.FEED.removeIf(f -> now - f.time() > 120 || now < f.time());
        for (ClientState.Feed f : ClientState.FEED) {
            String a = f.killer(), b = " 擊倒了 ", c = f.role();
            int x = w - 8 - width(a + b + c);
            text(g, a, x, y, f.mine() ? AMBER : TEAL, false);
            text(g, b, x + width(a), y, GRAY, false);
            text(g, c, x + width(a + b), y, PINK, false);
            y += 11;
        }
    }

    static void center(GuiGraphics g, int w, int h, long now) {
        if (now - ClientState.bigKillTime < 30 && now >= ClientState.bigKillTime)
            text(g, ClientState.bigKill, w / 2, h / 2 + 22, PINK, true);
        Gear.Med m = ClientState.healMed;
        if (m != null) {
            float left = Math.max(0, ClientState.healTotal - (now - ClientState.healStart)) / 20f;
            float v = 1 - left * 20f / ClientState.healTotal;
            text(g, m.verb + "  " + String.format("%.1f", left) + "s", w / 2, h / 2 + 36, WHITE, true);
            bar(g, w / 2 - 40, h / 2 + 47, 80, 3, v, TEAL);
        }
    }

    static float durability(ItemStack s) {
        if (s.isEmpty()) return -1;
        if (!s.isDamageableItem() || s.getMaxDamage() <= 0) return 1;
        return 1 - (float) s.getDamageValue() / s.getMaxDamage();
    }

    static void health(GuiGraphics g, LocalPlayer p, int h) {
        int x = 8, y = h - 50, wdt = 110;
        g.fill(x - 4, y - 4, x + wdt + 4, h - 4, PANEL);
        int hp = Math.round(p.getHealth() / p.getMaxHealth() * 100);
        big(g, String.valueOf(hp), x, y, hp > 30 ? WHITE : PINK, 2f);
        text(g, "生命", x + width(String.valueOf(hp)) * 2 + 4, y + 7, GRAY, false);
        bar(g, x, y + 19, wdt, 4, p.getHealth() / p.getMaxHealth(), hp > 30 ? WHITE : RED);
        float helm = durability(p.getItemBySlot(EquipmentSlot.HEAD)), vest = durability(p.getItemBySlot(EquipmentSlot.CHEST));
        int half = wdt / 2 - 3;
        text(g, "頭盔", x, y + 27, GRAY, false);
        bar(g, x, y + 37, half, 3, Math.max(0, helm), helm < 0 ? DIM : BLUE);
        text(g, "防彈衣", x + half + 6, y + 27, GRAY, false);
        bar(g, x + half + 6, y + 37, half, 3, Math.max(0, vest), vest < 0 ? DIM : BLUE);
        if (p.hasEffect(MobEffects.MOVEMENT_SLOWDOWN) && p.hasEffect(MobEffects.DIG_SLOWDOWN))
            text(g, "寒冷：移動變慢", x, y - 16, BLUE, false);
    }

    static void slots(GuiGraphics g, LocalPlayer p, int w, int h) {
        Inventory inv = p.getInventory();
        int[] slots = {0, 1, Gear.SLOT_GRENADE, Gear.SLOT_MED};
        String[] names = {"1 主武器", "2 副武器", "4 投擲", "5 醫療"};
        int bw = 64, bh = 26, gap = 3, x0 = w / 2 - (bw * 4 + gap * 3) / 2, y = h - bh - 6;
        for (int i = 0; i < 4; i++) {
            int x = x0 + i * (bw + gap);
            boolean sel = inv.selected == slots[i];
            g.fill(x, y, x + bw, y + bh, sel ? 0xCC141A22 : PANEL);
            box(g, x, y, bw, bh, sel ? WHITE : 0x55FFFFFF);
            text(g, names[i], x + 4, y + 3, GRAY, false);
            ItemStack s = inv.getItem(slots[i]);
            String line;
            if (i == 2) {
                Gear.Grenade gr = ClientState.grenade;
                ItemStack shown = Gear.Grenade.of(s) != null ? s : new ItemStack(gr.item());
                Gear.Grenade cur = Gear.Grenade.of(shown);
                int n = cur == null ? 0 : ClientInput.count(inv, cur);
                line = (cur == null ? gr.label : cur.label).split(" ")[0] + " ×" + n;
                if (n > 0) g.renderItem(shown, x + bw - 18, y + 9);
            } else if (i == 3) {
                int n = 0;
                for (Gear.Med m : Gear.Med.values()) n += ClientInput.count(inv, m);
                Gear.Med m = Gear.Med.of(s);
                line = (m == null ? "醫療" : m.label) + " ×" + n;
                if (!s.isEmpty()) g.renderItem(s, x + bw - 18, y + 9);
            } else {
                line = s.isEmpty() ? "—" : s.getHoverName().getString();
                if (!s.isEmpty()) g.renderItem(s, x + bw - 18, y + 9);
            }
            while (width(line) > bw - 22 && line.length() > 1) line = line.substring(0, line.length() - 1);
            text(g, line, x + 4, y + 14, WHITE, false);
        }
    }
}
