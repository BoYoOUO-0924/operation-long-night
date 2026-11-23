package dev.longnight.lnai.client;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.util.Mth;

/**
 * 章節標題卡：/lnhud title <玩家> <停留 tick> <AARRGGBB> <標題|副標>
 * 原版 /title 放大四倍後陰影（與粗體的重複描字）會變成明顯的重影，所以自己畫：不加陰影、不加粗。
 */
public final class TitleCard {
    private TitleCard() {}

    private static final int IN = 20, OUT = 30;
    private static String title = "", sub = "";
    private static int color = 0xFFFFB020, stay = 100;
    private static long start = -10000;

    /** 由 Net.Music 轉來：spec = "stay:AARRGGBB:標題|副標" */
    public static void set(String spec) {
        String[] a = spec.split(":", 3);
        stay = Integer.parseInt(a[0]);
        color = (int) Long.parseLong(a[1], 16);
        String[] t = a[2].split("\\|", 2);
        title = t[0];
        sub = t.length > 1 ? t[1] : "";
        start = ClientState.now();
    }

    static void draw(GuiGraphics g, int w, int h, float pt) {
        float age = ClientState.now() - start + pt;
        if (age < 0 || age > IN + stay + OUT || title.isEmpty()) return;
        float f = age < IN ? age / IN : age > IN + stay ? 1 - (age - IN - stay) / OUT : 1;
        f = Mth.clamp(f, 0, 1);
        Font font = Minecraft.getInstance().font;
        g.fill(0, h / 2 - 46, w, h / 2 + 26, Hud.fade(0x90000000, f));          // 淡淡的黑色橫帶墊底，取代陰影
        line(g, font, Hud.t(title), w / 2, h / 2 - 36, 3.0f, Hud.fade(color, f));
        if (!sub.isEmpty()) line(g, font, Hud.t(sub), w / 2, h / 2 + 4, 1.5f, Hud.fade(0xFFC8D0D8, f));
    }

    private static void line(GuiGraphics g, Font font, MutableComponent c, int cx, int y, float scale, int col) {
        g.pose().pushPose();
        g.pose().translate(cx - font.width(c) * scale / 2f, y, 0);
        g.pose().scale(scale, scale, 1);
        g.drawString(font, c, 0, 0, col, false);
        g.pose().popPose();
    }
}
