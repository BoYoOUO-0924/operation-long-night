package dev.longnight.lnai.client;

import dev.longnight.lnai.LnAi;
import dev.longnight.lnai.Net;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderLevelStageEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Matrix4f;
import org.joml.Vector4f;

/**
 * 真人隊友頭上的標記：P 色小三角形＋名字＋距離，隔牆也看得到。
 * 每一幀在世界繪製時記下鏡頭矩陣，HUD 再用它把隊友頭頂的位置換算成螢幕座標。
 */
@Mod.EventBusSubscriber(modid = LnAi.MODID, value = Dist.CLIENT)
public final class MateMarkers {
    private MateMarkers() {}

    private static final Matrix4f VIEW = new Matrix4f(), PROJ = new Matrix4f();
    private static Vec3 cam = Vec3.ZERO;
    private static boolean ready = false;

    @SubscribeEvent
    public static void capture(RenderLevelStageEvent e) {
        if (e.getStage() != RenderLevelStageEvent.Stage.AFTER_PARTICLES) return;
        VIEW.set(e.getPoseStack().last().pose());
        PROJ.set(e.getProjectionMatrix());
        cam = e.getCamera().getPosition();
        ready = true;
    }

    static void draw(GuiGraphics g, int w, int h, float pt) {
        if (!ready || CutscenePlayer.active()) return;
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer p = mc.player;
        if (p == null) return;
        for (Net.Mate m : Hud.mates(p)) {
            if (m.dead()) continue;
            Vec3 pos = Hud.matePos(m, pt).add(0, m.downed() ? 1.0 : 2.25, 0);
            double dist = pos.distanceTo(p.getEyePosition(pt));
            if (dist < 4 && !m.downed()) continue;   // 太近就不擋畫面（倒地的一定顯示）
            Vector4f v = new Vector4f((float) (pos.x - cam.x), (float) (pos.y - cam.y), (float) (pos.z - cam.z), 1);
            VIEW.transform(v);
            PROJ.transform(v);
            if (v.w <= 0.05f) continue;   // 在背後
            float sx = (v.x / v.w + 1) / 2 * w, sy = (1 - v.y / v.w) / 2 * h;
            if (sx < -20 || sx > w + 20 || sy < -20 || sy > h + 20) continue;
            int c = Hud.pcol(m.idx());
            float a = (float) Math.max(0.55, 1 - dist / 160);   // 越遠越淡
            int x = Math.round(sx), y = Math.round(sy);
            if (m.downed()) {   // 倒地：閃爍的紅色十字＋秒數
                boolean on = (ClientState.now() / 6) % 2 == 0;
                Hud.text(g, "✚", x + 1, y - 4, on ? 0xFFFF6A5A : 0xFFFFB0A0, true);
                Hud.small(g, m.name() + " 倒地 " + m.bleedSec() + "s", x + 1, y - 12, 0xFFFFB0A0, true);
            } else {
                Hud.text(g, "▼", x + 1, y - 4, Hud.fade(c, a), true);
                Hud.small(g, m.name() + " " + Math.round(dist) + "M", x + 1, y - 12, Hud.fade(c, a * 0.9f), true);
            }
        }
    }
}
