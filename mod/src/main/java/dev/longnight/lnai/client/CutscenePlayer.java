package dev.longnight.lnai.client;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import dev.longnight.lnai.LnAi;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Marker;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderGuiOverlayEvent;
import net.minecraftforge.client.event.RenderHandEvent;
import net.minecraftforge.client.event.RenderNameTagEvent;
import net.minecraftforge.client.event.ViewportEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.Event;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * 過場動畫（玩家端）：照伺服器送來的過場檔移動鏡頭、畫上下黑邊、字幕、淡入淡出。
 *
 * 做法：放一個不在世界裡的 Marker 當攝影機（mc.setCameraEntity），每 tick 把它移到路線上的位置；
 * 角度、視角大小、翻滾每一格畫面依時間精確計算。播放時開一個不暫停遊戲的畫面（CutsceneScreen），
 * 順便擋住移動和視角操作；HUD、手、名牌全部隱藏。
 */
@Mod.EventBusSubscriber(modid = LnAi.MODID, value = Dist.CLIENT)
public final class CutscenePlayer {
    private CutscenePlayer() {}

    record Key(int t, Vec3 pos, float yaw, float pitch, float roll, float fov, Vec3 look, boolean cut, boolean linear) {}

    record Sub(int at, int dur, String who, int color, String text) {}

    private static List<Key> keys = List.of();
    private static List<Sub> subs = List.of();
    private static int length, fadeIn, fadeOut, tick;
    private static float bar;
    private static Marker cam;
    private static CameraType savedCamera;
    private static boolean playing;

    public static boolean active() { return playing; }

    // ---------------- 開始／結束 ----------------
    public static void start(String json) {
        Minecraft mc = Minecraft.getInstance();
        if (json.isEmpty()) { end(); return; }
        if (mc.level == null || mc.player == null) return;
        JsonObject o = JsonParser.parseString(json).getAsJsonObject();
        keys = parseKeys(o.has("camera") ? o.getAsJsonArray("camera") : new JsonArray());
        subs = parseSubs(o.has("subtitles") ? o.getAsJsonArray("subtitles") : new JsonArray());
        fadeIn = o.has("fade_in") ? o.get("fade_in").getAsInt() : 15;
        fadeOut = o.has("fade_out") ? o.get("fade_out").getAsInt() : 15;
        bar = o.has("letterbox") ? o.get("letterbox").getAsFloat() : 0.11f;
        length = 0;
        for (Key k : keys) length = Math.max(length, k.t);
        for (Sub s : subs) length = Math.max(length, s.at + s.dur);
        tick = 0;

        if (!playing) savedCamera = mc.options.getCameraType();
        mc.options.setCameraType(CameraType.FIRST_PERSON);
        if (!keys.isEmpty()) {
            cam = new Marker(EntityType.MARKER, mc.level);
            place(0);
            place(0);   // 兩次：讓上一格位置也在起點，第一格不會從玩家位置滑過去
            mc.setCameraEntity(cam);
        }
        playing = true;
        mc.setScreen(new CutsceneScreen());
    }

    static void end() {
        Minecraft mc = Minecraft.getInstance();
        if (!playing) return;
        playing = false;
        if (mc.player != null) mc.setCameraEntity(mc.player);
        if (savedCamera != null) mc.options.setCameraType(savedCamera);
        cam = null;
        if (mc.screen instanceof CutsceneScreen) mc.setScreen(null);
    }

    // ---------------- 解析 ----------------
    private static List<Key> parseKeys(JsonArray a) {
        List<Key> out = new ArrayList<>();
        Key prev = null;
        for (JsonElement e : a) {
            JsonObject k = e.getAsJsonObject();
            Vec3 pos = vec(k, "pos", prev == null ? Vec3.ZERO : prev.pos);
            Vec3 look = k.has("look_at") ? vec(k, "look_at", null) : null;
            float yaw = f(k, "yaw", prev == null ? 0 : prev.yaw), pitch = f(k, "pitch", prev == null ? 0 : prev.pitch);
            if (look != null) { float[] yp = aim(pos, look); yaw = yp[0]; pitch = yp[1]; }
            Key key = new Key(k.get("t").getAsInt(), pos, yaw, pitch, f(k, "roll", 0), f(k, "fov", prev == null ? 70 : prev.fov),
                    look, k.has("cut") && k.get("cut").getAsBoolean(), k.has("ease") && k.get("ease").getAsString().equals("linear"));
            out.add(key);
            prev = key;
        }
        out.sort((x, y) -> Integer.compare(x.t, y.t));
        return out;
    }

    private static List<Sub> parseSubs(JsonArray a) {
        List<Sub> out = new ArrayList<>();
        for (JsonElement e : a) {
            JsonObject s = e.getAsJsonObject();
            int color = 0xFFE4E2DA;
            if (s.has("color")) {
                String c = s.get("color").getAsString().replace("#", "");
                try { color = 0xFF000000 | Integer.parseInt(c, 16); } catch (NumberFormatException ignored) {}
            }
            out.add(new Sub(s.get("at").getAsInt(), s.has("dur") ? s.get("dur").getAsInt() : 60,
                    s.has("who") ? s.get("who").getAsString() : "", color, s.get("text").getAsString()));
        }
        return out;
    }

    private static Vec3 vec(JsonObject o, String k, Vec3 def) {
        if (!o.has(k)) return def;
        JsonArray a = o.getAsJsonArray(k);
        return new Vec3(a.get(0).getAsDouble(), a.get(1).getAsDouble(), a.get(2).getAsDouble());
    }

    private static float f(JsonObject o, String k, float def) { return o.has(k) ? o.get(k).getAsFloat() : def; }

    /** 從 from 看向 to 的 yaw、pitch（Minecraft 慣例：yaw 0 = 南，pitch 正 = 往下） */
    static float[] aim(Vec3 from, Vec3 to) {
        Vec3 d = to.subtract(from);
        float yaw = (float) Math.toDegrees(Math.atan2(-d.x, d.z));
        float pitch = (float) -Math.toDegrees(Math.atan2(d.y, Math.sqrt(d.x * d.x + d.z * d.z)));
        return new float[]{yaw, pitch};
    }

    // ---------------- 路線計算 ----------------
    /** 時間 t（可以有小數）時的鏡頭狀態：x y z yaw pitch roll fov */
    static double[] sample(double t) {
        if (keys.isEmpty()) return null;
        int n = keys.size();
        if (t <= keys.get(0).t) return state(keys.get(0));
        if (t >= keys.get(n - 1).t) return state(keys.get(n - 1));
        int i = 0;
        while (i < n - 2 && keys.get(i + 1).t <= t) i++;
        Key a = keys.get(i), b = keys.get(i + 1);
        if (b.cut) return state(a);   // 下一個是切鏡：在切之前停在這一格
        double u = (t - a.t) / Math.max(1, b.t - a.t);
        double e = b.linear ? u : u * u * (3 - 2 * u);   // 預設緩進緩出
        Key p0 = i > 0 && !a.cut ? keys.get(i - 1) : a;
        Key p3 = i + 2 < n && !keys.get(i + 2).cut ? keys.get(i + 2) : b;
        Vec3 pos = catmull(p0.pos, a.pos, b.pos, p3.pos, e);
        float yaw, pitch;
        if (a.look != null && b.look != null) {   // 兩格都有注視點：沿路一直盯著（注視點本身也可以移動）
            float[] yp = aim(pos, a.look.lerp(b.look, e));
            yaw = yp[0]; pitch = yp[1];
        } else {
            yaw = (float) (a.yaw + Mth.wrapDegrees(b.yaw - a.yaw) * e);
            pitch = (float) Mth.lerp(e, a.pitch, b.pitch);
        }
        return new double[]{pos.x, pos.y, pos.z, yaw, pitch, Mth.lerp(e, a.roll, b.roll), Mth.lerp(e, a.fov, b.fov)};
    }

    private static double[] state(Key k) { return new double[]{k.pos.x, k.pos.y, k.pos.z, k.yaw, k.pitch, k.roll, k.fov}; }

    private static Vec3 catmull(Vec3 p0, Vec3 p1, Vec3 p2, Vec3 p3, double t) {
        double t2 = t * t, t3 = t2 * t;
        return new Vec3(cm(p0.x, p1.x, p2.x, p3.x, t, t2, t3), cm(p0.y, p1.y, p2.y, p3.y, t, t2, t3), cm(p0.z, p1.z, p2.z, p3.z, t, t2, t3));
    }

    private static double cm(double a, double b, double c, double d, double t, double t2, double t3) {
        return 0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t2 + (-a + 3 * b - 3 * c + d) * t3);
    }

    /** 攝影機實體：上一格 = 目前位置，這一格 = 時間 t 的位置。畫面在兩格之間內插，所以很順。 */
    private static void place(int t) {
        // 切鏡：切之前那一 tick 停在舊鏡頭的終點，切之後那一 tick 直接從新鏡頭起點開始，不要滑過去
        double[] s = sample(cutAt(t) ? t - 0.001 : t);
        if (s == null || cam == null) return;
        if (cutAt(t - 1)) {
            double[] c = sample(t - 1);
            cam.setPosRaw(c[0], c[1], c[2]);
        }
        cam.xo = cam.getX(); cam.yo = cam.getY(); cam.zo = cam.getZ();
        cam.xOld = cam.xo; cam.yOld = cam.yo; cam.zOld = cam.zo;
        cam.setPosRaw(s[0], s[1], s[2]);
        cam.setYRot((float) s[3]); cam.setXRot((float) s[4]);
        cam.yRotO = cam.getYRot(); cam.xRotO = cam.getXRot();
    }

    private static boolean cutAt(int t) {
        for (Key k : keys) if (k.cut && k.t == t) return true;
        return false;
    }

    // ---------------- 事件 ----------------
    @SubscribeEvent
    public static void onTick(TickEvent.ClientTickEvent e) {
        if (e.phase != TickEvent.Phase.END || !playing) return;
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || mc.level == null) { playing = false; cam = null; return; }
        if (tick >= length) { end(); return; }
        tick++;
        place(tick);   // 這一 tick 結束時鏡頭應該在 tick 的位置；畫面從上一格內插過來
        if (cam != null && mc.getCameraEntity() != cam) mc.setCameraEntity(cam);
        if (!(mc.screen instanceof CutsceneScreen) && mc.screen == null) mc.setScreen(new CutsceneScreen());
    }

    /** 畫面上的時間：上一 tick + 這一格的進度 */
    static double now(float partial) { return Math.min(length, tick - 1 + partial); }

    @SubscribeEvent
    public static void angles(ViewportEvent.ComputeCameraAngles e) {
        if (!playing || cam == null) return;
        double[] s = sample(now((float) e.getPartialTick()));
        e.setYaw((float) s[3]);
        e.setPitch((float) s[4]);
        e.setRoll((float) s[5]);
    }

    @SubscribeEvent
    public static void fov(ViewportEvent.ComputeFov e) {
        if (!playing || cam == null || !e.usedConfiguredFov()) return;
        e.setFOV(sample(now((float) e.getPartialTick()))[6]);
    }

    @SubscribeEvent(priority = EventPriority.HIGHEST)
    public static void hand(RenderHandEvent e) { if (playing) e.setCanceled(true); }

    @SubscribeEvent(priority = EventPriority.HIGHEST)
    public static void overlays(RenderGuiOverlayEvent.Pre e) { if (playing) e.setCanceled(true); }

    @SubscribeEvent
    public static void nameTags(RenderNameTagEvent e) { if (playing) e.setResult(Event.Result.DENY); }

    // ---------------- 畫面：黑邊、字幕、淡入淡出 ----------------
    static final class CutsceneScreen extends Screen {
        CutsceneScreen() { super(Component.empty()); }

        @Override public boolean isPauseScreen() { return false; }

        @Override public boolean shouldCloseOnEsc() { return false; }

        @Override
        protected void init() {   // 開畫面會放開滑鼠，把游標藏起來
            org.lwjgl.glfw.GLFW.glfwSetInputMode(Minecraft.getInstance().getWindow().getWindow(),
                    org.lwjgl.glfw.GLFW.GLFW_CURSOR, org.lwjgl.glfw.GLFW.GLFW_CURSOR_HIDDEN);
        }

        @Override
        public void render(GuiGraphics g, int mx, int my, float partial) {
            if (!playing) { onClose(); return; }
            int w = width, h = height;
            double t = now(partial);
            // 上下黑邊：開頭 12 tick 滑進來，結尾 12 tick 滑出去
            float k = (float) Mth.clamp(Math.min(t / 12.0, (length - t) / 12.0), 0, 1);
            k = k * k * (3 - 2 * k);
            int bh = Math.round(h * bar * k);
            if (bh > 0) {
                g.fill(0, 0, w, bh, 0xFF000000);
                g.fill(0, h - bh, w, h, 0xFF000000);
            }
            // 字幕：在下方黑邊裡置中；前後 5 tick 淡入淡出
            for (Sub s : subs) {
                double age = t - s.at;
                if (age < 0 || age > s.dur) continue;
                float a = (float) Mth.clamp(Math.min(age / 5.0, (s.dur - age) / 5.0), 0, 1);
                drawSub(g, s, w, h - Math.max(bh, Math.round(h * 0.11f)) / 2, a);
            }
            // 全畫面淡入淡出
            float black = 0;
            if (fadeIn > 0 && t < fadeIn) black = (float) (1 - t / fadeIn);
            if (fadeOut > 0 && t > length - fadeOut) black = Math.max(black, (float) ((t - (length - fadeOut)) / fadeOut));
            if (black > 0.004f) g.fill(0, 0, w, h, ((int) (Mth.clamp(black, 0, 1) * 255) << 24));
        }

        private void drawSub(GuiGraphics g, Sub s, int w, int y, float a) {
            int alpha = Math.max(4, Math.round(a * 255)) << 24;
            String name = s.who.isEmpty() ? "" : Hud.norm(s.who) + "   ";
            String text = Hud.norm(s.text);
            int nw = name.isEmpty() ? 0 : Hud.width(name), tw = Hud.width(text);
            float sc = 1.35f;   // 字幕比介面文字大一點
            g.pose().pushPose();
            g.pose().translate(w / 2f, y, 0);
            g.pose().scale(sc, sc, 1);
            int x = -(nw + tw) / 2;
            if (!name.isEmpty()) Hud.text(g, name, x, -4, alpha | (s.color & 0xFFFFFF), false);
            Hud.text(g, text, x + nw, -4, alpha | 0xF2F0EA, false);
            g.pose().popPose();
        }
    }
}
