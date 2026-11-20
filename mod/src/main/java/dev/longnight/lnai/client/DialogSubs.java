package dev.longnight.lnai.client;

import java.util.ArrayList;
import java.util.List;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.Mth;

/**
 * 遊玩中的對白字幕：畫面中下方、半透明黑底條，名字上色、台詞白字。
 * 最多同時兩句，新的一句在下面、舊的往上推，各自時間到就淡出。
 */
public final class DialogSubs {
    private DialogSubs() {}

    private record Line(String who, int color, String text, long at, int dur) {}

    private static final List<Line> LINES = new ArrayList<>();
    private static final int MAX = 2;
    private static final float SCALE = 1.25f;

    public static void add(String who, int color, String text, int dur) {
        LINES.add(new Line(who, color, text, ClientState.now(), dur));
        while (LINES.size() > MAX) LINES.remove(0);
    }

    static void draw(GuiGraphics g, int w, int h, float pt) {
        if (LINES.isEmpty()) return;
        long now = ClientState.now();
        LINES.removeIf(l -> now - l.at > l.dur);
        if (LINES.isEmpty() || CutscenePlayer.active()) return;
        Font f = Minecraft.getInstance().font;
        int maxW = Math.round(Math.min(w * 0.62f, 420) / SCALE);   // 一行最寬（縮放前）
        g.pose().pushPose();
        g.pose().translate(w / 2f, h - 62, 0);
        g.pose().scale(SCALE, SCALE, 1);
        int y = 0;   // 從最下面一句往上排
        for (int i = LINES.size() - 1; i >= 0; i--) {
            Line l = LINES.get(i);
            double age = now - l.at + pt;
            float a = (float) Mth.clamp(Math.min(age / 4.0, (l.dur - age) / 8.0), 0, 1);
            if (a <= 0.02f) continue;
            String name = l.who.isEmpty() ? "" : Hud.norm(l.who) + "  ";
            int nw = name.isEmpty() ? 0 : Hud.width(name);
            List<FormattedCharSequence> rows = f.split(Hud.t(l.text), Math.max(60, maxW - nw));
            int tw = 0;
            for (FormattedCharSequence r : rows) tw = Math.max(tw, f.width(r));
            int bw = nw + tw, rowH = 11, bh = rows.size() * rowH;
            y -= bh;
            int x = -bw / 2;
            g.fill(x - 6, y - 3, x + bw + 6, y + bh + 1, Hud.fade(0x8C000000, a));
            if (!name.isEmpty()) Hud.text(g, name, x, y, Hud.fade(0xFF000000 | l.color, a), false);
            for (int k = 0; k < rows.size(); k++)
                g.drawString(f, rows.get(k), x + nw, y + k * rowH, Hud.fade(0xFFF2F0EA, a), true);
            y -= 7;   // 兩句之間的間距
        }
        g.pose().popPose();
    }
}
