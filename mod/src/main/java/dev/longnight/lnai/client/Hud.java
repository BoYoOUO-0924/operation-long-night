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
import net.minecraft.util.Mth;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.CustomizeGuiOverlayEvent;
import net.minecraftforge.client.event.RegisterGuiOverlaysEvent;
import net.minecraftforge.client.event.RenderGuiOverlayEvent;
import net.minecraftforge.client.gui.overlay.VanillaGuiOverlay;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * 戰術介面（寫實風）：頂部方位羅盤（隊友、目標）、左上目標、右上敵軍兵力、左側小隊狀態、
 * 左下生命與護甲、下方固定物品欄（選中為黃色）。彈藥沿用 TaCZ 自己的顯示。
 */
public final class Hud {
    private Hud() {}

    static final int SHADE = 0x80101418, SHADE_LIGHT = 0x50101418, DIM = 0x40FFFFFF, WHITE = 0xFFFFFFFF, GRAY = 0xFFB8BCC2,
            AMBER = 0xFFF2C230, AMBER_DARK = 0xFF2A2208, TEAL = 0xFF5DCAA5, ORANGE = 0xFFEF9F27, RED = 0xFFE24B4A,
            PINK = 0xFFF09595, BLUE = 0xFF6FA8E8;

    /** 小隊：名字、圖示（unifont 字元）。 */
    static final String[][] SQUAD = {{"白鴉", "⌖"}, {"戰車", "⛨"}, {"狐狸", "≋"}};

    // ---------- 字型與繪圖小工具 ----------
    /** 全形標點在 Rajdhani／思源黑體混排時間距會跑掉，換成半形。 */
    static String norm(String s) {
        return s.replace("：", ": ").replace("！", "! ").replace("，", ", ").replace("？", "? ");
    }

    static MutableComponent t(String s) { return Component.literal(norm(s)).withStyle(st -> st.withFont(LnAi.FONT)); }

    static int width(String s) { return Minecraft.getInstance().font.width(t(s)); }

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

    static void small(GuiGraphics g, String s, int x, int y, int color, boolean centered) {
        g.pose().pushPose();
        g.pose().translate(x, y, 0);
        g.pose().scale(0.75f, 0.75f, 1);
        text(g, s, 0, 0, color, centered);
        g.pose().popPose();
    }

    /** 粗線條：底下一條深色陰影，讓雪地上也看得到。 */
    static void bar(GuiGraphics g, int x, int y, int w, int h, float v, int color) {
        g.fill(x - 1, y - 1, x + w + 1, y + h + 1, 0x90000000);
        g.fill(x, y, x + w, y + h, DIM);
        g.fill(x, y, x + Math.round(w * Mth.clamp(v, 0, 1)), y + h, color);
    }

    static void box(GuiGraphics g, int x, int y, int w, int h, int color) {
        g.fill(x, y, x + w, y + 1, color);
        g.fill(x, y + h - 1, x + w, y + h, color);
        g.fill(x, y, x + 1, y + h, color);
        g.fill(x + w - 1, y, x + w, y + h, color);
    }

    static boolean active() { return ClientInput.active(Minecraft.getInstance().player); }

    static String pad3(int n) { return String.format("%03d", Math.max(0, n)); }

    // ---------- 註冊與隱藏原版 ----------
    @Mod.EventBusSubscriber(modid = LnAi.MODID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.MOD)
    public static final class Setup {
        @SubscribeEvent
        public static void overlays(RegisterGuiOverlaysEvent e) {
            e.registerAboveAll("ln_hud", (gui, g, pt, w, h) -> { if (active()) draw(g, w, h); });
        }
    }

    static Component bossName = null;
    static long bossAt = -100;

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

        /** 聊天（對白）往上移，避開左下的生命面板。 */
        @SubscribeEvent
        public static void chat(CustomizeGuiOverlayEvent.Chat e) {
            if (active()) e.setPosY(e.getPosY() - 64);
        }

        /** 王條（敵軍剩餘兵力）不畫在中間，改成右上角一行字。 */
        @SubscribeEvent
        public static void boss(CustomizeGuiOverlayEvent.BossEventProgress e) {
            if (!active()) return;
            e.setCanceled(true);
            e.setIncrement(0);
            bossName = e.getBossEvent().getName();
            bossAt = ClientState.now();
        }
    }

    // ---------- 主畫面 ----------
    static void draw(GuiGraphics g, int w, int h) {
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer p = mc.player;
        long now = ClientState.now();
        float s = Math.min(1f, w / 560f);   // 介面太窄時整體縮小
        g.pose().pushPose();
        g.pose().scale(s, s, 1);
        w = Math.round(w / s);
        h = Math.round(h / s);
        refreshSquad(p, now);
        compass(g, p, w);
        objective(g, p);
        enemies(g, w, now);
        squad(g, p);
        feed(g, w, h, now);
        center(g, w, h, now);
        health(g, p, h);
        slots(g, p, w, h);
        g.pose().popPose();
    }

    // ---- 頂部方位羅盤 ----
    static final int COMPASS_W = 240, SPAN = 120;   // 寬度、可見角度

    /** 水平方位角：0 = 北，90 = 東。 */
    static float heading(LocalPlayer p) { return Mth.wrapDegrees(p.getYRot() + 180f) < 0 ? Mth.wrapDegrees(p.getYRot() + 180f) + 360 : Mth.wrapDegrees(p.getYRot() + 180f); }

    static float bearing(Vec3 from, Vec3 to) {
        float b = (float) Math.toDegrees(Math.atan2(to.x - from.x, -(to.z - from.z)));
        return b < 0 ? b + 360 : b;
    }

    static void compass(GuiGraphics g, LocalPlayer p, int w) {
        int cx = w / 2, y = 10;
        float head = heading(p), ppd = COMPASS_W / (float) SPAN;
        g.fill(cx - COMPASS_W / 2, y + 6, cx + COMPASS_W / 2, y + 7, 0x60FFFFFF);
        String[] names = {"N", "NE", "E", "SE", "S", "SW", "W", "NW"};
        for (int d = 0; d < 360; d += 15) {
            float delta = Mth.wrapDegrees(d - head);
            if (Math.abs(delta) > SPAN / 2f) continue;
            int x = cx + Math.round(delta * ppd);
            int alpha = (int) (255 * (1 - Math.abs(delta) / (SPAN / 2f) * 0.7f));
            int col = (alpha << 24) | 0xFFFFFF;
            if (d % 45 == 0) {
                g.fill(x, y + 2, x + 1, y + 7, col);
                text(g, names[d / 45], x + 1, y - 8, col, true);
            } else {
                g.fill(x, y + 4, x + 1, y + 7, col);
                if (d % 30 == 0) small(g, pad3(d), x + 1, y - 6, (alpha * 3 / 4 << 24) | 0xFFFFFF, true);
            }
        }
        text(g, "▼", cx + 1, y + 8, AMBER, true);
        Vec3 eye = p.position();
        // 隊友
        for (String[] m : SQUAD) {
            LivingEntity e = find(m[0]);
            if (e != null) marker(g, cx, y, ppd, head, bearing(eye, e.position()), m[1], m[0], TEAL);
        }
        // 目標
        if (ClientState.waypoint != null)
            marker(g, cx, y, ppd, head, bearing(eye, ClientState.waypoint), "◆", "OBJ " + Math.round(Math.sqrt(p.distanceToSqr(ClientState.waypoint))) + "M", AMBER);
    }

    static void marker(GuiGraphics g, int cx, int y, float ppd, float head, float bearing, String icon, String label, int color) {
        float delta = Mth.wrapDegrees(bearing - head);
        boolean edge = Math.abs(delta) > SPAN / 2f;
        float d = Mth.clamp(delta, -SPAN / 2f, SPAN / 2f);
        int x = cx + Math.round(d * ppd);
        int col = edge ? (color & 0x00FFFFFF) | 0x90000000 : color;
        text(g, edge ? (delta < 0 ? "◀" : "▶") : icon, x + 1, y + 18, col, true);
        if (!edge) small(g, label, x + 1, y + 29, col, true);
    }

    // ---- 左上目標 ----
    static void objective(GuiGraphics g, LocalPlayer p) {
        if (ClientState.objective.isEmpty()) return;
        int x = 10, y = 10;
        g.fill(x - 4, y - 3, x - 2, y + 21, AMBER);
        String line = "OBJ // " + ClientState.objective;
        Font f = Minecraft.getInstance().font;
        var lines = f.split(t(line), 170);
        for (var l : lines) { g.drawString(f, l, x, y, WHITE, true); y += 10; }
        if (ClientState.waypoint != null)
            text(g, "距離 " + Math.round(Math.sqrt(p.distanceToSqr(ClientState.waypoint))) + "M", x, y + 1, AMBER, false);
    }

    // ---- 右上敵軍兵力 ----
    static void enemies(GuiGraphics g, int w, long now) {
        if (bossName == null || now - bossAt > 5 || now < bossAt) return;
        String s = norm(bossName.getString()).trim();
        int x = w - 10 - width(s);
        text(g, "●", x - 9, 10, RED, false);
        text(g, s, x, 10, WHITE, false);
    }

    // ---- 左側小隊狀態 ----
    private static final List<LivingEntity> squadCache = new ArrayList<>();
    private static long squadAt = -100;

    static void refreshSquad(LocalPlayer p, long now) {
        if (now - squadAt <= 10 && now >= squadAt) return;
        squadAt = now;
        squadCache.clear();
        for (Entity e : Minecraft.getInstance().level.entitiesForRendering())
            if (e instanceof LivingEntity le && le != p && le.hasCustomName()) {
                String n = le.getCustomName().getString();
                for (String[] s : SQUAD) if (s[0].equals(n)) squadCache.add(le);
            }
    }

    static LivingEntity find(String name) {
        for (LivingEntity e : squadCache) if (e.isAlive() && e.getCustomName().getString().equals(name)) return e;
        return null;
    }

    static void squad(GuiGraphics g, LocalPlayer p) {
        if (squadCache.isEmpty()) return;
        int x = 10, y = 64, rowW = 112;
        small(g, "獵犬小隊", x, y, GRAY, false);
        y += 9;
        for (String[] m : SQUAD) {
            LivingEntity e = find(m[0]);
            g.fill(x, y, x + rowW, y + 18, SHADE);
            g.fill(x, y, x + 16, y + 18, 0x60FFFFFF);
            text(g, m[1], x + 8, y + 5, e == null ? 0xFF777777 : WHITE, true);
            text(g, m[0], x + 20, y + 2, e == null ? 0xFF777777 : WHITE, false);
            if (e == null) { right(g, "—", x + rowW - 4, y + 2, GRAY); y += 21; continue; }
            right(g, String.format("%02dM", Math.min(99, Math.round(e.distanceTo(p)))), x + rowW - 4, y + 2, GRAY);
            float v = e.getHealth() / e.getMaxHealth();
            bar(g, x + 20, y + 12, rowW - 24, 2, v, v > 0.6f ? TEAL : v > 0.3f ? ORANGE : RED);
            y += 21;
        }
    }

    // ---- 右側擊殺紀錄 ----
    static void feed(GuiGraphics g, int w, int h, long now) {
        int y = 40;
        ClientState.FEED.removeIf(f -> now - f.time() > 120 || now < f.time());
        for (ClientState.Feed f : ClientState.FEED) {
            String a = f.killer(), b = "  ✕  ", c = f.role();
            int x = w - 10 - width(a + b + c);
            g.fill(x - 4, y - 2, w - 6, y + 10, SHADE_LIGHT);
            text(g, a, x, y, f.mine() ? AMBER : TEAL, false);
            text(g, b, x + width(a), y, GRAY, false);
            text(g, c, x + width(a + b), y, PINK, false);
            y += 13;
        }
    }

    static void center(GuiGraphics g, int w, int h, long now) {
        if (now - ClientState.bigKillTime < 30 && now >= ClientState.bigKillTime)
            text(g, ClientState.bigKill, w / 2, h / 2 + 22, PINK, true);
        if (now - ClientState.arcTime <= 1 && now >= ClientState.arcTime)
            text(g, ClientState.arcDist < 0 ? "落點 —" : "落點 " + Math.round(ClientState.arcDist) + "M", w / 2, h / 2 + 12, WHITE, true);
        Gear.Med m = ClientState.healMed;
        if (m != null) {
            float left = Math.max(0, ClientState.healTotal - (now - ClientState.healStart)) / 20f;
            float v = 1 - left * 20f / ClientState.healTotal;
            text(g, m.verb + "  " + String.format("%.1f", left) + "s", w / 2, h / 2 + 36, WHITE, true);
            bar(g, w / 2 - 40, h / 2 + 47, 80, 3, v, TEAL);
        }
    }

    // ---- 左下生命與護甲 ----
    static float durability(ItemStack s) {
        if (s.isEmpty()) return -1;
        if (!s.isDamageableItem() || s.getMaxDamage() <= 0) return 1;
        return 1 - (float) s.getDamageValue() / s.getMaxDamage();
    }

    static void health(GuiGraphics g, LocalPlayer p, int h) {
        int x = 10, y = h - 54, wdt = 120;
        g.fill(x - 6, y - 6, x + wdt + 6, h - 6, SHADE_LIGHT);
        int hp = Math.round(p.getHealth() / p.getMaxHealth() * 100);
        int col = hp > 30 ? WHITE : PINK;
        big(g, String.valueOf(hp), x, y, col, 2.2f);
        int nx = x + Math.round(width(String.valueOf(hp)) * 2.2f) + 3;
        text(g, "/ 100", nx, y + 4, GRAY, false);
        small(g, "HP", nx, y + 14, GRAY, false);
        bar(g, x, y + 24, wdt, 3, p.getHealth() / p.getMaxHealth(), hp > 30 ? WHITE : RED);
        float helm = durability(p.getItemBySlot(EquipmentSlot.HEAD)), vest = durability(p.getItemBySlot(EquipmentSlot.CHEST));
        small(g, "防彈衣", x, y + 31, GRAY, false);
        bar(g, x + 30, y + 32, wdt - 30, 3, Math.max(0, vest), vest < 0 ? DIM : BLUE);
        small(g, "頭盔", x, y + 40, GRAY, false);
        bar(g, x + 30, y + 41, wdt - 30, 3, Math.max(0, helm), helm < 0 ? DIM : BLUE);
        if (p.hasEffect(MobEffects.MOVEMENT_SLOWDOWN) && p.hasEffect(MobEffects.DIG_SLOWDOWN))
            text(g, "❄ 寒冷：移動變慢", x, y - 18, BLUE, false);
    }

    // ---- 下方固定物品欄 ----
    static void slots(GuiGraphics g, LocalPlayer p, int w, int h) {
        Inventory inv = p.getInventory();
        int[] slots = {0, 1, Gear.SLOT_GRENADE, Gear.SLOT_MED};
        String[] keys = {"1", "2", "4", "5"};
        int bw = 66, bh = 22, gap = 3, x0 = Math.max(150, w / 2 - (bw * 4 + gap * 3) / 2), y = h - bh - 8;
        for (int i = 0; i < 4; i++) {
            int x = x0 + i * (bw + gap);
            boolean sel = inv.selected == slots[i];
            g.fill(x, y, x + bw, y + bh, sel ? 0xE0F2C230 : SHADE);
            if (!sel) g.fill(x, y + bh - 1, x + bw, y + bh, 0x40FFFFFF);
            int fg = sel ? AMBER_DARK : WHITE, sub = sel ? AMBER_DARK : GRAY;
            ItemStack s = inv.getItem(slots[i]);
            String line;
            ItemStack icon = s;
            if (i == 2) {
                Gear.Grenade cur = Gear.Grenade.of(s);
                if (cur == null) { cur = ClientState.grenade; icon = new ItemStack(cur.item()); }
                line = cur.label.split(" ")[0] + " ×" + ClientInput.count(inv, cur);
            } else if (i == 3) {
                int n = 0;
                for (Gear.Med m : Gear.Med.values()) n += ClientInput.count(inv, m);
                Gear.Med m = Gear.Med.of(s);
                line = (m == null ? "醫療" : m.label) + " ×" + n;
            } else {
                line = s.isEmpty() ? "—" : s.getHoverName().getString();
            }
            small(g, keys[i], x + 3, y + 2, sub, false);
            if (!icon.isEmpty()) g.renderItem(icon, x + 3, y + 5);
            while (width(line) > bw - 25 && line.length() > 1) line = line.substring(0, line.length() - 1);
            g.drawString(Minecraft.getInstance().font, t(line), x + 22, y + 8, fg, !sel);
        }
    }
}
