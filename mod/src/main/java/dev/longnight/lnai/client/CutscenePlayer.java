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

    /** player = 這一格是「玩家自己的眼睛」（位置、角度、視角大小都跟玩家一樣，用來把鏡頭交還給玩家）；
     *  fov 是 NaN = 用玩家設定的視角；handheld = 手持晃動幅度（度） */
    record Key(int t, Vec3 pos, float yaw, float pitch, float roll, float fov, Vec3 look, boolean cut, boolean linear,
               boolean player, float handheld) {}

    record Shake(int at, int dur, float amp) {}

    /** 畫面中央的大標題（章節名稱）：text 大字、sub 小字 */
    record Title(int at, int dur, String text, String sub) {}

    record Sub(int at, int dur, String who, int color, String text) {}

    private static List<Key> keys = List.of();
    private static List<Sub> subs = List.of();
    private static List<Shake> shakes = List.of();
    private static List<Title> titles = List.of();
    private static int frostTotal, frostLeft;
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
        List<Shake> sh = new ArrayList<>();
        if (o.has("shakes")) for (JsonElement el : o.getAsJsonArray("shakes")) {
            JsonObject so = el.getAsJsonObject();
            sh.add(new Shake(so.get("at").getAsInt(), so.has("dur") ? so.get("dur").getAsInt() : 5, f(so, "amp", 1.5f)));
        }
        shakes = sh;
        List<Title> ti = new ArrayList<>();
        if (o.has("titles")) for (JsonElement el : o.getAsJsonArray("titles")) {
            JsonObject to = el.getAsJsonObject();
            ti.add(new Title(to.get("at").getAsInt(), to.has("dur") ? to.get("dur").getAsInt() : 80,
                    to.get("text").getAsString(), to.has("sub") ? to.get("sub").getAsString() : ""));
        }
        titles = ti;
        frostTotal = o.has("frost_after") ? o.get("frost_after").getAsInt() : 0;
        frostLeft = 0;
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
        frostLeft = frostTotal;
        if (mc.screen instanceof CutsceneScreen) mc.setScreen(null);
    }

    // ---------------- 解析 ----------------
    private static List<Key> parseKeys(JsonArray a) {
        List<Key> out = new ArrayList<>();
        Key prev = null;
        for (JsonElement e : a) {
            JsonObject k = e.getAsJsonObject();
            boolean player = k.has("pos") && k.get("pos").isJsonPrimitive() && k.get("pos").getAsString().equals("player");
            Vec3 pos = player ? Vec3.ZERO : vec(k, "pos", prev == null ? Vec3.ZERO : prev.pos);
            Vec3 look = k.has("look_at") ? vec(k, "look_at", null) : null;
            float yaw = f(k, "yaw", prev == null ? 0 : prev.yaw), pitch = f(k, "pitch", prev == null ? 0 : prev.pitch);
            if (look != null) { float[] yp = aim(pos, look); yaw = yp[0]; pitch = yp[1]; }
            float fov = k.has("fov") && k.get("fov").isJsonPrimitive() && k.get("fov").getAsJsonPrimitive().isString()
                    ? Float.NaN : f(k, "fov", prev == null ? 70 : prev.fov);
            if (player) { look = null; fov = Float.NaN; }
            Key key = new Key(k.get("t").getAsInt(), pos, yaw, pitch, f(k, "roll", 0), fov,
                    look, k.has("cut") && k.get("cut").getAsBoolean(), k.has("ease") && k.get("ease").getAsString().equals("linear"),
                    player, f(k, "handheld", prev == null ? 0 : prev.handheld));
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
        if (!o.has(k) || !o.get(k).isJsonArray()) return def;
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

    // ---------------- 「玩家」關鍵格：每次計算時才讀玩家目前的位置與角度 ----------------
    private static float partialNow;

    private static Vec3 kpos(Key k) {
        if (!k.player) return k.pos;
        var p = Minecraft.getInstance().player;
        return p == null ? k.pos : p.getEyePosition(partialNow);
    }

    private static float kyaw(Key k) { var p = Minecraft.getInstance().player; return k.player && p != null ? p.getViewYRot(partialNow) : k.yaw; }

    private static float kpitch(Key k) { var p = Minecraft.getInstance().player; return k.player && p != null ? p.getViewXRot(partialNow) : k.pitch; }

    private static float kfov(Key k) { return Float.isNaN(k.fov) ? Minecraft.getInstance().options.fov().get() : k.fov; }

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
        Vec3 pos = catmull(kpos(p0), kpos(a), kpos(b), kpos(p3), e);
        float yaw, pitch;
        if (a.look != null && b.look != null) {   // 兩格都有注視點：沿路一直盯著（注視點本身也可以移動）
            float[] yp = aim(pos, a.look.lerp(b.look, e));
            yaw = yp[0]; pitch = yp[1];
        } else {
            yaw = (float) (kyaw(a) + Mth.wrapDegrees(kyaw(b) - kyaw(a)) * e);
            pitch = (float) Mth.lerp(e, kpitch(a), kpitch(b));
        }
        return new double[]{pos.x, pos.y, pos.z, yaw, pitch, Mth.lerp(e, a.roll, b.roll), Mth.lerp(e, kfov(a), kfov(b)),
                Mth.lerp(u, a.handheld, b.handheld)};
    }

    private static double[] state(Key k) {
        Vec3 p = kpos(k);
        return new double[]{p.x, p.y, p.z, kyaw(k), kpitch(k), k.roll, kfov(k), k.handheld};
    }

    /** 手持晃動（幾個不同頻率的正弦波疊加）＋ 短促震動，回傳 yaw、pitch、roll 的偏移 */
    private static float[] wobble(double t, double amp) {
        float sy = 0, sp = 0, sr = 0;
        if (amp > 0) {
            sy = (float) (amp * (Math.sin(t * 0.37) * 0.6 + Math.sin(t * 0.91 + 1.3) * 0.3 + Math.sin(t * 2.3 + 0.4) * 0.1));
            sp = (float) (amp * (Math.sin(t * 0.53 + 2.1) * 0.6 + Math.sin(t * 1.27 + 0.7) * 0.3 + Math.sin(t * 2.9) * 0.1));
            sr = (float) (amp * 0.5 * Math.sin(t * 0.29 + 0.5));
        }
        for (Shake s : shakes) {
            double age = t - s.at;
            if (age < 0 || age > s.dur) continue;
            double k = s.amp * (1 - age / s.dur);
            sp += (float) (k * Math.sin(age * 3.1));
            sy += (float) (k * 0.4 * Math.sin(age * 4.3 + 1));
        }
        return new float[]{sy, sp, sr};
    }

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
        for (Sub s : subs) if (s.at == tick) Voice.play(s.who, s.text, true);   // 字幕出現時播對應的語音
        place(tick);   // 這一 tick 結束時鏡頭應該在 tick 的位置；畫面從上一格內插過來
        if (cam != null && mc.getCameraEntity() != cam) mc.setCameraEntity(cam);
        if (!(mc.screen instanceof CutsceneScreen) && mc.screen == null) mc.setScreen(new CutsceneScreen());
    }

    /** 畫面上的時間：上一 tick + 這一格的進度 */
    static double now(float partial) { return Math.min(length, tick - 1 + partial); }

    @SubscribeEvent
    public static void angles(ViewportEvent.ComputeCameraAngles e) {
        if (!playing || cam == null) return;
        partialNow = (float) e.getPartialTick();
        double t = now(partialNow);
        double[] s = sample(t);
        float[] w = wobble(t, s[7]);
        e.setYaw((float) s[3] + w[0]);
        e.setPitch((float) s[4] + w[1]);
        e.setRoll((float) s[5] + w[2]);
    }

    @SubscribeEvent
    public static void fov(ViewportEvent.ComputeFov e) {
        if (!playing || cam == null || !e.usedConfiguredFov()) return;
        e.setFOV(sample(now((float) e.getPartialTick()))[6]);
    }

    @SubscribeEvent(priority = EventPriority.HIGHEST)
    public static void hand(RenderHandEvent e) { if (playing) e.setCanceled(true); }

    // ---------------- 過場結束後的冰霜外框（原版細雪結凍的畫面） ----------------
    private static final net.minecraft.resources.ResourceLocation FROST = new net.minecraft.resources.ResourceLocation("textures/misc/powder_snow_outline.png");

    @SubscribeEvent
    public static void frost(net.minecraftforge.client.event.RenderGuiEvent.Post e) {
        if (frostLeft <= 0 || playing) return;
        float a = (float) frostLeft / Math.max(1, frostTotal);
        a = Math.min(1f, a * 1.6f);   // 前段維持滿，後段淡出
        GuiGraphics g = e.getGuiGraphics();
        int w = g.guiWidth(), h = g.guiHeight();
        com.mojang.blaze3d.systems.RenderSystem.enableBlend();
        g.setColor(1f, 1f, 1f, a);
        g.blit(FROST, 0, 0, -90, 0f, 0f, w, h, w, h);
        g.setColor(1f, 1f, 1f, 1f);
        com.mojang.blaze3d.systems.RenderSystem.disableBlend();
    }

    @SubscribeEvent
    public static void frostTick(TickEvent.ClientTickEvent e) {
        if (e.phase == TickEvent.Phase.END && frostLeft > 0 && !playing) frostLeft--;
    }

    @SubscribeEvent(priority = EventPriority.HIGHEST)
    public static void overlays(RenderGuiOverlayEvent.Pre e) { if (playing) e.setCanceled(true); }

    @SubscribeEvent
    public static void nameTags(RenderNameTagEvent e) { if (playing) e.setResult(Event.Result.DENY); }

    /** 過場中不畫其他真人玩家（他們站在開場位置，會擋住鏡頭）；鏡頭衝進自己眼睛時也不畫自己（不然會看到頭部模型的內側） */
    @SubscribeEvent
    public static void hideSelf(net.minecraftforge.client.event.RenderPlayerEvent.Pre e) {
        Minecraft mc = Minecraft.getInstance();
        if (!playing || cam == null) return;
        if (e.getEntity() != mc.player || cam.position().distanceTo(mc.player.getEyePosition()) < 2.5) e.setCanceled(true);
    }

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
            // 章節大標題：前後 15 tick 淡入淡出
            for (Title ti : titles) {
                double age = t - ti.at;
                if (age < 0 || age > ti.dur) continue;
                float a = (float) Mth.clamp(Math.min(age / 15.0, (ti.dur - age) / 15.0), 0, 1);
                int alpha = Math.max(4, Math.round(a * 255)) << 24;
                g.pose().pushPose();
                g.pose().translate(w / 2f, h * 0.42f, 0);
                g.pose().scale(2.6f, 2.6f, 1);
                Hud.text(g, ti.text, 0, -4, alpha | 0xF2F0EA, true, false);
                g.pose().popPose();
                if (!ti.sub.isEmpty()) {
                    g.pose().pushPose();
                    g.pose().translate(w / 2f, h * 0.42f + 22, 0);
                    g.pose().scale(1.2f, 1.2f, 1);
                    Hud.text(g, ti.sub, 0, -4, alpha | 0xC8D0D8, true, false);
                    g.pose().popPose();
                }
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
