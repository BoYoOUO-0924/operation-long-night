package dev.longnight.lnai;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.mojang.logging.LogUtils;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.server.packs.resources.SimpleJsonResourceReloadListener;
import net.minecraft.util.profiling.ProfilerFiller;
import net.minecraftforge.event.AddReloadListenerEvent;
import net.minecraftforge.event.TickEvent;
import org.slf4j.Logger;

/**
 * 過場動畫（伺服器端）。
 *
 * 檔案放在資料包 data/<命名空間>/cutscenes/<名稱>.json，/reload 就會重新讀取。
 * 播放：/lnhud cutscene <玩家> <命名空間:名稱>；中止：/lnhud cutscene <玩家> stop
 *
 * 伺服器負責：把整個過場檔送給玩家（鏡頭、字幕由玩家端播放）、照時間執行 "commands"、
 * 播放期間讓玩家無敵（"protect": false 可關閉）。格式見 docs/過場動畫.md。
 */
final class Cutscenes {
    private Cutscenes() {}

    private static final Logger LOG = LogUtils.getLogger();
    private static final Gson GSON = new Gson();
    private static final Map<ResourceLocation, JsonObject> DEFS = new HashMap<>();

    private record Cmd(int at, String run) {}

    /** NPC 走位：tag 的實體在 at～at+dur 之間沿著 path 等速走完（ground = 自動貼地），面向前進方向 */
    private record Move(int at, int dur, String tag, List<net.minecraft.world.phys.Vec3> path, boolean ground) {}

    private static final class Running {
        final List<Cmd> cmds;
        final List<Move> moves = new ArrayList<>();
        final List<String> freeze = new ArrayList<>();
        final List<net.minecraft.world.entity.Mob> frozen = new ArrayList<>();
        final List<UUID> viewers;
        final CommandSourceStack src;
        final int length;
        final boolean protect;
        int t = 0;

        Running(List<Cmd> cmds, List<UUID> viewers, CommandSourceStack src, int length, boolean protect) {
            this.cmds = cmds; this.viewers = viewers; this.src = src; this.length = length; this.protect = protect;
        }
    }

    private static final List<Running> RUNNING = new ArrayList<>();
    /** 播放前就已經無敵的玩家（例如創造模式），結束時不要幫他們關掉 */
    private static final java.util.Set<UUID> WAS_INVULNERABLE = new java.util.HashSet<>();

    static void onReload(AddReloadListenerEvent e) {
        e.addListener(new SimpleJsonResourceReloadListener(GSON, "cutscenes") {
            @Override
            protected void apply(Map<ResourceLocation, JsonElement> files, ResourceManager rm, ProfilerFiller pf) {
                DEFS.clear();
                files.forEach((id, el) -> { if (el.isJsonObject()) DEFS.put(id, el.getAsJsonObject()); });
                LOG.info("[lnai] loaded {} cutscenes: {}", DEFS.size(), DEFS.keySet());
            }
        });
    }

    static Collection<ResourceLocation> names() { return DEFS.keySet(); }

    /** 過場的總長度（tick）：最後一個鏡頭關鍵格、字幕結束、指令的最大值 */
    static int length(JsonObject def) {
        int len = 0;
        if (def.has("camera")) for (JsonElement k : def.getAsJsonArray("camera")) len = Math.max(len, k.getAsJsonObject().get("t").getAsInt());
        if (def.has("subtitles")) for (JsonElement s : def.getAsJsonArray("subtitles")) {
            JsonObject o = s.getAsJsonObject();
            len = Math.max(len, o.get("at").getAsInt() + (o.has("dur") ? o.get("dur").getAsInt() : 60));
        }
        return len;
    }

    static int play(CommandSourceStack src, Collection<ServerPlayer> ps, ResourceLocation id) {
        JsonObject def = DEFS.get(id);
        if (def == null) { src.sendFailure(net.minecraft.network.chat.Component.literal("找不到過場 " + id + "（有：" + DEFS.keySet() + "）")); return 0; }
        int len = length(def);
        boolean protect = !def.has("protect") || def.get("protect").getAsBoolean();
        List<Cmd> cmds = new ArrayList<>();
        if (def.has("commands")) for (JsonElement c : def.getAsJsonArray("commands")) {
            JsonObject o = c.getAsJsonObject();
            cmds.add(new Cmd(o.get("at").getAsInt(), o.get("run").getAsString()));
            len = Math.max(len, o.get("at").getAsInt());
        }
        List<Move> moves = new ArrayList<>();
        for (JsonElement m : arr(def, "moves")) {
            JsonObject o = m.getAsJsonObject();
            List<net.minecraft.world.phys.Vec3> path = new ArrayList<>();
            for (JsonElement pt : o.getAsJsonArray("path")) {
                JsonArray a = pt.getAsJsonArray();
                path.add(new net.minecraft.world.phys.Vec3(a.get(0).getAsDouble(), a.get(1).getAsDouble(), a.get(2).getAsDouble()));
            }
            moves.add(new Move(o.get("at").getAsInt(), o.get("dur").getAsInt(), o.get("tag").getAsString(), path,
                    !o.has("ground") || o.get("ground").getAsBoolean()));
            len = Math.max(len, o.get("at").getAsInt() + o.get("dur").getAsInt());
        }
        // 玩家端只需要鏡頭和字幕，指令留在伺服器
        JsonObject toClient = def.deepCopy();
        toClient.remove("commands");
        toClient.remove("moves");
        toClient.remove("freeze");
        String json = GSON.toJson(toClient);
        List<UUID> viewers = new ArrayList<>();
        for (ServerPlayer p : ps) {
            stopFor(p);
            viewers.add(p.getUUID());
            if (protect) setProtected(p, true);
            Net.to(p, new Net.Cutscene(json));
        }
        Running run = new Running(cmds, viewers, src.withSuppressedOutput().withPermission(2), len, protect);
        run.moves.addAll(moves);
        for (JsonElement f : arr(def, "freeze")) run.freeze.add(f.getAsString());
        // 被凍結的 NPC 在過場期間不跑 AI（不會自己亂走、轉頭、開槍），由 moves 和指令控制
        for (net.minecraft.world.entity.Entity e : src.getLevel().getAllEntities())
            if (e instanceof net.minecraft.world.entity.Mob mob && !mob.isNoAi() && run.freeze.stream().anyMatch(t -> e.getTags().contains(t))) {
                mob.setNoAi(true);
                run.frozen.add(mob);
            }
        RUNNING.add(run);
        runDue(RUNNING.get(RUNNING.size() - 1));   // at = 0 的指令立刻執行
        return ps.size();
    }

    static int stop(Collection<ServerPlayer> ps) {
        for (ServerPlayer p : ps) {
            stopFor(p);
            Net.to(p, new Net.Cutscene(""));
        }
        // 沒有人在看的過場整個取消：剩下的指令不再執行（例如過場結尾的「進入第 1 階段」），凍結的 NPC 解凍
        RUNNING.removeIf(r -> {
            if (!r.viewers.isEmpty()) return false;
            for (net.minecraft.world.entity.Mob mob : r.frozen) if (mob.isAlive()) mob.setNoAi(false);
            return true;
        });
        return ps.size();
    }

    private static void stopFor(ServerPlayer p) {
        for (Running r : RUNNING) if (r.viewers.remove(p.getUUID()) && r.protect) setProtected(p, false);
    }

    private static void setProtected(ServerPlayer p, boolean on) {
        if (on) {
            if (p.getAbilities().invulnerable) WAS_INVULNERABLE.add(p.getUUID());
            p.getAbilities().invulnerable = true;
        } else if (!WAS_INVULNERABLE.remove(p.getUUID())) {
            p.getAbilities().invulnerable = p.isCreative() || p.isSpectator();
        }
        p.onUpdateAbilities();
    }

    private static void runDue(Running r) {
        for (Cmd c : r.cmds) if (c.at == r.t) {
            try { r.src.getServer().getCommands().performPrefixedCommand(r.src, c.run); }
            catch (Exception ex) { LOG.warn("[lnai] cutscene command failed: {} ({})", c.run, ex.toString()); }
        }
    }

    static void tick(MinecraftServer server) {
        if (RUNNING.isEmpty()) return;
        RUNNING.removeIf(r -> {
            r.t++;
            runDue(r);
            moveAll(r);
            if (r.t < r.length) return false;
            for (net.minecraft.world.entity.Mob mob : r.frozen) if (mob.isAlive()) mob.setNoAi(false);
            for (UUID u : r.viewers) {
                ServerPlayer p = server.getPlayerList().getPlayer(u);
                if (p != null && r.protect) setProtected(p, false);
            }
            return true;
        });
    }

    private static void moveAll(Running r) {
        for (Move m : r.moves) {
            if (r.t < m.at || r.t > m.at + m.dur) continue;
            double u = (r.t - m.at) / (double) Math.max(1, m.dur);
            // 依路徑長度找出目前位置
            double total = 0;
            for (int i = 1; i < m.path.size(); i++) total += m.path.get(i).distanceTo(m.path.get(i - 1));
            double want = u * total;
            net.minecraft.world.phys.Vec3 pos = m.path.get(0), dir = m.path.size() > 1 ? m.path.get(1).subtract(m.path.get(0)) : null;
            for (int i = 1; i < m.path.size(); i++) {
                net.minecraft.world.phys.Vec3 a = m.path.get(i - 1), b = m.path.get(i);
                double seg = b.distanceTo(a);
                dir = b.subtract(a);
                if (want <= seg || i == m.path.size() - 1) { pos = a.lerp(b, seg == 0 ? 1 : Math.min(1, want / seg)); break; }
                want -= seg;
            }
            net.minecraft.server.level.ServerLevel level = r.src.getLevel();
            double y = pos.y;
            if (m.ground) {
                net.minecraft.core.BlockPos bp = net.minecraft.core.BlockPos.containing(pos.x, pos.y + 3, pos.z);
                for (int i = 0; i < 8 && level.getBlockState(bp).getCollisionShape(level, bp).isEmpty(); i++) bp = bp.below();
                var shape = level.getBlockState(bp).getCollisionShape(level, bp);
                y = shape.isEmpty() ? pos.y : bp.getY() + shape.max(net.minecraft.core.Direction.Axis.Y);
            }
            float yaw = dir == null || dir.horizontalDistanceSqr() < 1e-6 ? 0 : (float) Math.toDegrees(Math.atan2(-dir.x, dir.z));
            for (net.minecraft.world.entity.Entity e : level.getAllEntities()) {
                if (!e.getTags().contains(m.tag)) continue;
                e.moveTo(pos.x, y, pos.z, yaw, 0);
                e.setYHeadRot(yaw);
                e.setYBodyRot(yaw);
            }
        }
    }

    static void onTick(TickEvent.ServerTickEvent e) {
        if (e.phase == TickEvent.Phase.END) tick(e.getServer());
    }

    static JsonArray arr(JsonObject o, String k) { return o.has(k) ? o.getAsJsonArray(k) : new JsonArray(); }
}
