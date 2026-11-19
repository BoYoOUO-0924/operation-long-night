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
 * 戰術介面（寫實風，低彩度，參考逃離塔科夫）：
 * 頂部方位羅盤、左上目標、右上敵軍兵力、左側小隊、左下生命與護甲圖示、右下彈藥、
 * 下方物品欄（只在任務開始、物品變動、切換時出現幾秒）。
 */
public final class Hud {
    private Hud() {}

    // 低彩度色盤
    static final int TEXT = 0xFFE4E2DA, SUB = 0xFFC8D0D8, FAINT = 0xFFA4ACB4, ACCENT = 0xFFB9AE8C, OBJ = 0xFFFFB020,
            OK = 0xFF9DB497, WARN = 0xFFD2AE62, BAD = 0xFFC8604F, STEEL = 0xFF8E9AA6,
            PANEL = 0x70000000, TRACK = 0x4DE6E6E6;

    /** 小隊：名字、圖示（unifont 字元）。 */
    static final String[][] SQUAD = {{"白鴉", "⌖"}, {"戰車", "⛨"}, {"狐狸", "≋"}};

    // ---------- 字型與繪圖小工具 ----------
    static String norm(String s) {
        return s.replace("：", ": ").replace("！", "! ").replace("，", ", ").replace("？", "? ");
    }

    static MutableComponent t(String s) { return Component.literal(norm(s)).withStyle(st -> st.withFont(LnAi.FONT)); }

    static int width(String s) { return Minecraft.getInstance().font.width(t(s)); }

    /** 依 f（0～1）調整顏色透明度，用於淡入淡出。 */
    static int fade(int color, float f) {
        int a = Math.round(((color >>> 24) & 0xFF) * Mth.clamp(f, 0, 1));
        return (Math.max(a, 4) << 24) | (color & 0xFFFFFF);
    }

    static void text(GuiGraphics g, String s, int x, int y, int color, boolean centered) {
        Font f = Minecraft.getInstance().font;
        MutableComponent c = t(s);
        g.drawString(f, c, centered ? x - f.width(c) / 2 : x, y, color, true);
    }

    static void right(GuiGraphics g, String s, int x, int y, int color) { text(g, s, x - width(s), y, color, false); }

    static void scaled(GuiGraphics g, String s, int x, int y, int color, float scale, boolean rightAlign) {
        g.pose().pushPose();
        g.pose().translate(x - (rightAlign ? width(s) * scale : 0), y, 0);
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

    static void bar(GuiGraphics g, int x, int y, int w, int h, float v, int color) {
        g.fill(x - 1, y - 1, x + w + 1, y + h + 1, 0x70000000);
        g.fill(x, y, x + w, y + h, TRACK);
        g.fill(x, y, x + Math.round(w * Mth.clamp(v, 0, 1)), y + h, color);
    }

    static void box(GuiGraphics g, int x, int y, int w, int h, int color) {
        g.fill(x, y, x + w, y + 1, color);
        g.fill(x, y + h - 1, x + w, y + h, color);
        g.fill(x, y, x + 1, y + h, color);
        g.fill(x + w - 1, y, x + w, y + h, color);
    }

    static void icon(GuiGraphics g, ItemStack s, int x, int y, float scale) {
        g.pose().pushPose();
        g.pose().translate(x, y, 0);
        g.pose().scale(scale, scale, 1);
        g.renderItem(s, 0, 0);
        g.pose().popPose();
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

        @SubscribeEvent
        public static void chat(CustomizeGuiOverlayEvent.Chat e) {
            if (active()) e.setPosY(e.getPosY() - 64);
        }

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
        float s = Math.min(1f, w / 560f);
        g.pose().pushPose();
        g.pose().scale(s, s, 1);
        w = Math.round(w / s);
        h = Math.round(h / s);
        refreshSquad(p, now);
        compass(g, p, w);
        objective(g, p);
        enemies(g, w, now);
        squad(g, p);
        feed(g, w, now);
        center(g, w, h, now);
        health(g, p, h);
        ammo(g, p, w, h);
        slots(g, p, w, h, now);
        g.pose().popPose();
    }

    // ---- 頂部方位羅盤 ----
    static final int COMPASS_W = 240, SPAN = 120;

    static float heading(LocalPlayer p) {
        float h = Mth.wrapDegrees(p.getYRot() + 180f);
        return h < 0 ? h + 360 : h;
    }

    static float bearing(Vec3 from, Vec3 to) {
        float b = (float) Math.toDegrees(Math.atan2(to.x - from.x, -(to.z - from.z)));
        return b < 0 ? b + 360 : b;
    }

    static void compass(GuiGraphics g, LocalPlayer p, int w) {
        int cx = w / 2, y = 10;
        float head = heading(p), ppd = COMPASS_W / (float) SPAN;
        g.fillGradient(0, 0, w, y + 46, 0x66000000, 0x00000000);   // 整條上緣淡出，任何天氣都看得清楚刻度
        g.fill(cx - COMPASS_W / 2, y + 6, cx + COMPASS_W / 2, y + 7, 0x80FFFFFF);
        String[] names = {"N", "NE", "E", "SE", "S", "SW", "W", "NW"};
        for (int d = 0; d < 360; d += 15) {
            float delta = Mth.wrapDegrees(d - head);
            if (Math.abs(delta) > SPAN / 2f) continue;
            int x = cx + Math.round(delta * ppd);
            float f = 1 - Math.abs(delta) / (SPAN / 2f) * 0.5f;
            if (d % 45 == 0) {
                g.fill(x, y + 2, x + 1, y + 7, fade(TEXT, f));
                text(g, names[d / 45], x + 1, y - 8, fade(TEXT, f), true);
            } else {
                g.fill(x, y + 4, x + 1, y + 7, fade(SUB, f));
                if (d % 30 == 0) small(g, pad3(d), x + 1, y - 6, fade(SUB, f), true);
            }
        }
        text(g, "▾", cx + 1, y + 8, TEXT, true);
        Vec3 eye = p.position();
        for (String[] m : SQUAD) {
            LivingEntity e = find(m[0]);
            if (e != null) marker(g, cx, y, ppd, head, bearing(eye, e.position()), m[1], m[0], OK);
        }
        if (ClientState.waypoint != null)
            marker(g, cx, y, ppd, head, bearing(eye, ClientState.waypoint), "◆", "OBJ " + Math.round(Math.sqrt(p.distanceToSqr(ClientState.waypoint))) + "M", OBJ);
    }

    static void marker(GuiGraphics g, int cx, int y, float ppd, float head, float bearing, String icon, String label, int color) {
        float delta = Mth.wrapDegrees(bearing - head);
        boolean edge = Math.abs(delta) > SPAN / 2f;
        int x = cx + Math.round(Mth.clamp(delta, -SPAN / 2f, SPAN / 2f) * ppd);
        int col = edge ? fade(color, 0.5f) : color;
        text(g, edge ? (delta < 0 ? "‹" : "›") : icon, x + 1, y + 18, col, true);
        if (!edge) small(g, label, x + 1, y + 29, fade(col, 0.85f), true);
    }

    // ---- 左上目標 ----
    static void objective(GuiGraphics g, LocalPlayer p) {
        if (ClientState.objective.isEmpty()) return;
        int x = 10, y = 10;
        g.fill(x - 4, y - 2, x - 3, y + 20, OBJ);
        small(g, "OBJ", x, y, OBJ, false);
        y += 8;
        Font f = Minecraft.getInstance().font;
        for (var l : f.split(t(ClientState.objective), 170)) { g.drawString(f, l, x, y, TEXT, true); y += 10; }
        if (ClientState.waypoint != null)
            small(g, Math.round(Math.sqrt(p.distanceToSqr(ClientState.waypoint))) + "M", x, y + 1, SUB, false);
    }

    // ---- 右上敵軍兵力 ----
    static void enemies(GuiGraphics g, int w, long now) {
        if (bossName == null || now - bossAt > 5 || now < bossAt) return;
        var m = java.util.regex.Pattern.compile("[0-9]+").matcher(bossName.getString());
        int[] n = {-1, -1};
        for (int i = 0; i < 2 && m.find(); i++) n[i] = Integer.parseInt(m.group());
        String s = n[1] >= 0 ? "敵軍剩餘兵力 " + pad3(n[0]) + "   |   場上 " + String.format("%02d", n[1]) : norm(bossName.getString()).trim();
        int x = w - 10 - width(s);
        diamond(g, x - 9, 13, 3, 0x40FF3B30);   // 微光
        diamond(g, x - 9, 13, 2, 0xFFE0403A);
        text(g, s, x, 10, SUB, false);
    }

    /** 實心菱形，中心 (cx, cy)，半徑 r。 */
    static void diamond(GuiGraphics g, int cx, int cy, int r, int color) {
        for (int i = -r; i <= r; i++) {
            int half = r - Math.abs(i);
            g.fill(cx - half, cy + i, cx + half + 1, cy + i + 1, color);
        }
    }

    // ---- 左側小隊 ----
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
        int x = 10, y = 60, rowW = 104;
        small(g, "SQUAD // 獵犬", x, y, FAINT, false);
        y += 9;
        for (String[] m : SQUAD) {
            LivingEntity e = find(m[0]);
            int fg = e == null ? FAINT : TEXT;
            g.fill(x, y, x + rowW, y + 17, PANEL);
            g.fill(x, y, x + 1, y + 17, e == null ? FAINT : SUB);
            text(g, m[1], x + 8, y + 4, e == null ? FAINT : TEXT, true);
            text(g, m[0], x + 17, y + 2, fg, false);
            if (e == null) { right(g, "—", x + rowW - 4, y + 2, FAINT); y += 19; continue; }
            small(g, String.format("%02dM", Math.min(99, Math.round(e.distanceTo(p)))), x + rowW - 4 - Math.round(width("00M") * 0.75f), y + 3, SUB, false);
            float v = e.getHealth() / e.getMaxHealth();
            bar(g, x + 17, y + 12, rowW - 21, 1, v, v > 0.6f ? OK : v > 0.3f ? WARN : BAD);
            y += 19;
        }
    }

    // ---- 右側擊殺紀錄 ----
    static void feed(GuiGraphics g, int w, long now) {
        int y = 26;
        ClientState.FEED.removeIf(f -> now - f.time() > 120 || now < f.time());
        for (ClientState.Feed f : ClientState.FEED) {
            String a = f.killer(), b = "  ✕  ", c = f.role();
            int x = w - 10 - width(a + b + c);
            float fd = Math.min(1f, (120 - (now - f.time())) / 20f);
            text(g, a, x, y, fade(f.mine() ? TEXT : SUB, fd), false);
            text(g, b, x + width(a), y, fade(FAINT, fd), false);
            text(g, c, x + width(a + b), y, fade(BAD, fd), false);
            y += 11;
        }
    }

    static void center(GuiGraphics g, int w, int h, long now) {
        if (now - ClientState.bigKillTime < 30 && now >= ClientState.bigKillTime)
            text(g, ClientState.bigKill, w / 2, h / 2 + 22, fade(TEXT, 1 - (now - ClientState.bigKillTime) / 30f), true);
        if (now - ClientState.arcTime <= 1 && now >= ClientState.arcTime)
            small(g, ClientState.arcDist < 0 ? "—" : Math.round(ClientState.arcDist) + "M", w / 2, h / 2 + 12, TEXT, true);
        Gear.Med m = ClientState.healMed;
        if (m != null) {
            float left = Math.max(0, ClientState.healTotal - (now - ClientState.healStart)) / 20f;
            float v = 1 - left * 20f / ClientState.healTotal;
            text(g, m.verb + "  " + String.format("%.1f", left) + "s", w / 2, h / 2 + 36, TEXT, true);
            bar(g, w / 2 - 40, h / 2 + 47, 80, 2, v, OK);
        }
    }

    // ---- 左下生命與護甲（圖示） ----
    static float durability(ItemStack s) {
        if (s.isEmpty()) return -1;
        if (!s.isDamageableItem() || s.getMaxDamage() <= 0) return 1;
        return 1 - (float) s.getDamageValue() / s.getMaxDamage();
    }

    static void health(GuiGraphics g, LocalPlayer p, int h) {
        int x = 12, y = h - 50;
        float hpv = p.getHealth() / p.getMaxHealth();
        int hp = Math.round(hpv * 100);
        int col = hp > 30 ? TEXT : BAD;
        String n = String.valueOf(hp);
        scaled(g, n, x, y, col, 2.2f, false);
        int nx = x + Math.round(width(n) * 2.2f) + 4;
        small(g, "HP", nx, y + 4, SUB, false);
        small(g, "/100", nx, y + 12, FAINT, false);
        bar(g, x, y + 22, 96, 2, hpv, hp > 30 ? TEXT : BAD);
        // 護甲：頭盔、防彈衣圖示（顏色＝耐久），右邊百分比
        ItemStack[] gear = {p.getItemBySlot(EquipmentSlot.HEAD), p.getItemBySlot(EquipmentSlot.CHEST)};
        net.minecraft.resources.ResourceLocation[] tex = {HELMET, VEST};
        for (int i = 0; i < 2; i++) {
            int gx = x + i * 50, gy = y + 29;
            float d = durability(gear[i]);
            int gc = d < 0 ? FAINT : d > 0.5f ? TEXT : d > 0.2f ? WARN : BAD;
            g.fill(gx, gy, gx + 46, gy + 18, PANEL);
            tinted(g, tex[i], gx + 2, gy + 1, 16, gc);
            small(g, d < 0 ? "—" : Math.round(d * 100) + "%", gx + 21, gy + 3, gc, false);
            bar(g, gx + 21, gy + 12, 21, 1, Math.max(0, d), gc);
        }
        // 異常狀態：亮藍色提示
        int sy = y - 16;
        if (p.hasEffect(MobEffects.MOVEMENT_SLOWDOWN) && p.hasEffect(MobEffects.DIG_SLOWDOWN))
            sy = status(g, "❄ 寒冷：移動變慢", x, sy);
    }

    static final net.minecraft.resources.ResourceLocation HELMET = new net.minecraft.resources.ResourceLocation(LnAi.MODID, "textures/gui/helmet.png"),
            VEST = new net.minecraft.resources.ResourceLocation(LnAi.MODID, "textures/gui/vest.png");
    static final int STATUS = 0xFF5BC0FF;

    static void tinted(GuiGraphics g, net.minecraft.resources.ResourceLocation tex, int x, int y, int size, int argb) {
        com.mojang.blaze3d.systems.RenderSystem.enableBlend();
        g.setColor(((argb >> 16) & 0xFF) / 255f, ((argb >> 8) & 0xFF) / 255f, (argb & 0xFF) / 255f, ((argb >>> 24) & 0xFF) / 255f);
        g.blit(tex, x, y, size, size, 0, 0, 32, 32, 32, 32);
        g.setColor(1, 1, 1, 1);
    }

    /** 狀態提示：亮藍字＋深色底，回傳下一個的 y（往上排）。 */
    static int status(GuiGraphics g, String s, int x, int y) {
        int w = width(s);
        g.fill(x - 2, y - 2, x + w + 3, y + 10, 0x90000814);
        g.fill(x - 2, y - 2, x - 1, y + 10, STATUS);
        text(g, s, x + 1, y, STATUS, false);
        return y - 14;
    }

    // ---- 右下彈藥 ----
    static final net.minecraft.resources.ResourceLocation GRENADE_ICON = new net.minecraft.resources.ResourceLocation(LnAi.MODID, "textures/gui/grenade.png"),
            MED_ICON = new net.minecraft.resources.ResourceLocation(LnAi.MODID, "textures/gui/med.png");

    static void ammo(GuiGraphics g, LocalPlayer p, int w, int h) {
        // 投擲物、醫療數量（一直顯示）：[4] 手雷 ×2   [5] 繃帶 ×8
        Inventory inv = p.getInventory();
        Gear.Grenade gr = ClientInput.pickGrenade(inv, ClientState.grenade);
        int gn = gr == null ? 0 : ClientInput.count(inv, gr), mn = 0;
        for (Gear.Med m : Gear.Med.values()) mn += ClientInput.count(inv, m);
        g.fillGradient(w - 150, h - 70, w, h, 0x00000000, 0x55000000);   // 右下淡淡的底，雪地上也看得清
        int qx = w - 12, qy = h - 14;
        String ms = "×" + mn, gs = "×" + gn;
        qx -= width(ms);
        text(g, ms, qx, qy, mn == 0 ? FAINT : TEXT, false);
        tinted(g, MED_ICON, qx - 12, qy - 1, 10, mn == 0 ? FAINT : TEXT);
        small(g, "5", qx - 19, qy + 1, SUB, false);
        qx -= 34 + width(gs);
        text(g, gs, qx, qy, gn == 0 ? FAINT : TEXT, false);
        tinted(g, GRENADE_ICON, qx - 12, qy - 1, 10, gn == 0 ? FAINT : TEXT);
        small(g, "4", qx - 19, qy + 1, SUB, false);

        Ammo.Info a = Ammo.of(p.getMainHandItem(), inv);
        if (a == null) return;
        int x = w - 12, y = h - 56;
        small(g, a.name() + (a.mode().isEmpty() ? "" : "  ·  " + a.mode()), x - Math.round(width(a.name() + (a.mode().isEmpty() ? "" : "  ·  " + a.mode())) * 0.75f), y, SUB, false);
        String res = a.reserve() < 0 ? "" : " / " + a.reserve();
        int rw = width(res);
        text(g, res, x - rw, y + 18, SUB, false);
        scaled(g, String.valueOf(a.mag()), x - rw - 1, y + 9, a.mag() == 0 ? BAD : TEXT, 2.2f, true);
    }

    // ---- 下方物品欄：任務開始、物品變動、切換時出現 3 秒 ----
    static long slotsUntil = -1;
    static String slotSig = "";

    static void pokeSlots() { slotsUntil = ClientState.now() + 70; }

    static void slots(GuiGraphics g, LocalPlayer p, int w, int h, long now) {
        Inventory inv = p.getInventory();
        StringBuilder sig = new StringBuilder().append(inv.selected);
        for (int i = 0; i <= Gear.LAST_SLOT; i++) { ItemStack s = inv.getItem(i); sig.append('|').append(s.getItem()).append(s.getCount()); }
        for (Gear.Med m : Gear.Med.values()) sig.append(ClientInput.count(inv, m));
        for (Gear.Grenade gr : Gear.Grenade.values()) sig.append(ClientInput.count(inv, gr));
        if (!sig.toString().equals(slotSig)) { slotSig = sig.toString(); pokeSlots(); }
        if (ClientState.healMed != null || Minecraft.getInstance().screen instanceof WheelScreen) slotsUntil = Math.max(slotsUntil, now + 20);
        if (now > slotsUntil || now < slotsUntil - 200) return;
        float f = Math.min(1f, (slotsUntil - now) / 15f);

        int[] slots = {0, 1, 2, Gear.SLOT_GRENADE, Gear.SLOT_MED};
        String[] keys = {"1", "2", "3", "4", "5"};
        String[] empty = {"主武器", "副武器", "近戰", "投擲", "醫療"};
        int bw = 62, bh = 22, gap = 2, x0 = w / 2 - (bw * 5 + gap * 4) / 2, y = h - bh - 10;
        for (int i = 0; i < 5; i++) {
            int x = x0 + i * (bw + gap);
            boolean sel = inv.selected == slots[i];
            g.fill(x, y, x + bw, y + bh, fade(sel ? 0x90202020 : PANEL, f));
            g.fill(x, y + bh - 1, x + bw, y + bh, fade(sel ? ACCENT : 0x30FFFFFF, f));
            if (sel) box(g, x, y, bw, bh, fade(0x60B9AE8C, f));
            ItemStack s = inv.getItem(slots[i]);
            ItemStack ic = s;
            String line;
            if (slots[i] == Gear.SLOT_GRENADE) {
                Gear.Grenade cur = Gear.Grenade.of(s);
                if (cur == null) { cur = ClientState.grenade; ic = new ItemStack(cur.item()); }
                int n = ClientInput.count(inv, cur);
                line = n == 0 ? "—" : cur.label.split(" ")[0] + " ×" + n;
                if (n == 0) ic = ItemStack.EMPTY;
            } else if (slots[i] == Gear.SLOT_MED) {
                int n = 0;
                for (Gear.Med m : Gear.Med.values()) n += ClientInput.count(inv, m);
                Gear.Med m = Gear.Med.of(s);
                line = n == 0 ? "—" : (m == null ? "醫療" : m.label) + " ×" + n;
            } else {
                line = s.isEmpty() ? empty[i] : s.getHoverName().getString();
            }
            int fg = fade(s.isEmpty() && slots[i] < Gear.SLOT_GRENADE ? FAINT : sel ? TEXT : SUB, f);
            small(g, keys[i], x + 3, y + 2, fade(sel ? ACCENT : FAINT, f), false);
            if (!ic.isEmpty() && f > 0.6f) icon(g, ic, x + 4, y + 6, 0.875f);
            while (width(line) > bw - 24 && line.length() > 1) line = line.substring(0, line.length() - 1);
            text(g, line, x + 21, y + 8, fg, false);
        }
    }
}
