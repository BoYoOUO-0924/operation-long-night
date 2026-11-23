package dev.longnight.lnai.client;

import net.minecraft.client.gui.GuiGraphics;

/**
 * 全螢幕色調（例如機艙切成戰鬥紅光）：/lnhud tint <玩家> <AARRGGBB> [淡入 tick] [pulse]
 * Minecraft 的方塊光沒有顏色，所以用畫面疊色模擬；pulse = 持續跟著警報閃爍（要用 00000000 關掉）；flash = 一次性閃光。
 */
public final class ScreenTint {
    private ScreenTint() {}

    private static int color = 0;          // 目標顏色（ARGB）
    private static float alpha = 0, target = 0, step = 1;
    private static boolean pulse;
    private static int age;
    private static int flashColor = 0;      // 一次性閃光（爆炸、被照到）：獨立一層，自己淡掉
    private static float flash = 0, flashStep = 0.05f;

    /** 由 Net.Music 轉來：spec = "AARRGGBB:fade:pulse" */
    public static void set(String spec) {
        String[] a = spec.split(":");
        long argb = Long.parseLong(a[0], 16);
        int fade = a.length > 1 ? Integer.parseInt(a[1]) : 20;
        if (a.length > 2 && a[2].equals("2")) {
            flashColor = (int) (argb & 0xFFFFFF);
            flash = ((argb >>> 24) & 0xFF) / 255f;
            flashStep = flash / Math.max(1, fade);
            return;
        }
        pulse = a.length > 2 && a[2].equals("1");
        float t = ((argb >>> 24) & 0xFF) / 255f;
        if (t > 0) color = (int) (argb & 0xFFFFFF);
        target = t;
        step = fade <= 0 ? 1 : Math.max(0.002f, Math.abs(target - alpha) / fade);
    }

    public static void tick() {
        age++;
        if (flash > 0) flash = Math.max(0, flash - flashStep);
        if (alpha < target) alpha = Math.min(target, alpha + step);
        else if (alpha > target) alpha = Math.max(target, alpha - step);
    }

    static void draw(GuiGraphics g, int w, int h, float pt) {
        if (flash > 0.001f) g.fill(0, 0, w, h, (Math.min(255, (int) (flash * 255)) << 24) | flashColor);
        if (alpha <= 0.001f) return;
        float a = alpha;
        if (pulse) a *= 0.65f + 0.35f * (float) Math.sin((age + pt) * Math.PI / 10.0);   // 約每秒閃一次
        int ai = Math.max(0, Math.min(255, (int) (a * 255)));
        g.fill(0, 0, w, h, (ai << 24) | color);
    }
}
