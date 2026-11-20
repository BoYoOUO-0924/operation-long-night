package dev.longnight.lnai;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.FloatArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.commands.arguments.ResourceLocationArgument;
import net.minecraft.commands.arguments.coordinates.Vec3Argument;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.registries.ForgeRegistries;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

/**
 * /lnhud objective <玩家> <文字>        設定畫面左上的目標（文字為空 = 清除）
 * /lnhud waypoint <玩家> <x y z> | clear  目標的導航點（顯示距離）
 * /lnhud cutscene <玩家> <名稱> | stop   播放／中止過場動畫（見 Cutscenes）
 * /lnhud anim <實體> <動作> | stop      讓 NPC（或玩家）播放角色動作（assets/lnai/player_animation/）
 * /lnhud trace <實體> <x y z> <vx> <vy>   測量拋射物軌跡（寫進伺服器紀錄，給拋物線預覽校正用）
 */
final class HudCommand {
    private HudCommand() {}

    private static final Logger LOG = LogUtils.getLogger();
    private static String lastText = "";
    private static Vec3 lastWp = null;

    static void register(RegisterCommandsEvent e) {
        CommandDispatcher<CommandSourceStack> d = e.getDispatcher();
        d.register(Commands.literal("lnhud").requires(s -> s.hasPermission(2))
                .then(Commands.literal("objective").then(Commands.argument("targets", EntityArgument.players())
                        .executes(c -> objective(EntityArgument.getPlayers(c, "targets"), ""))
                        .then(Commands.argument("text", StringArgumentType.greedyString())
                                .executes(c -> objective(EntityArgument.getPlayers(c, "targets"), StringArgumentType.getString(c, "text"))))))
                .then(Commands.literal("waypoint").then(Commands.argument("targets", EntityArgument.players())
                        .then(Commands.literal("clear").executes(c -> waypoint(EntityArgument.getPlayers(c, "targets"), null)))
                        .then(Commands.argument("pos", Vec3Argument.vec3())
                                .executes(c -> waypoint(EntityArgument.getPlayers(c, "targets"), Vec3Argument.getVec3(c, "pos"))))))
                .then(Commands.literal("cutscene").then(Commands.argument("targets", EntityArgument.players())
                        .then(Commands.literal("stop").executes(c -> Cutscenes.stop(EntityArgument.getPlayers(c, "targets"))))
                        .then(Commands.argument("name", ResourceLocationArgument.id())
                                .suggests((c, b) -> net.minecraft.commands.SharedSuggestionProvider.suggestResource(Cutscenes.names(), b))
                                .executes(c -> Cutscenes.play(c.getSource(), EntityArgument.getPlayers(c, "targets"), ResourceLocationArgument.getId(c, "name"))))))
                .then(Commands.literal("anim").then(Commands.argument("targets", EntityArgument.entities())
                        .then(Commands.argument("name", StringArgumentType.word())
                                .executes(c -> anim(EntityArgument.getEntities(c, "targets"), StringArgumentType.getString(c, "name"))))))
                .then(Commands.literal("trace").then(Commands.argument("type", ResourceLocationArgument.id())
                        .then(Commands.argument("pos", Vec3Argument.vec3())
                                .then(Commands.argument("vx", FloatArgumentType.floatArg())
                                        .then(Commands.argument("vy", FloatArgumentType.floatArg())
                                                .executes(c -> trace(c.getSource(), ResourceLocationArgument.getId(c, "type"),
                                                        Vec3Argument.getVec3(c, "pos"), FloatArgumentType.getFloat(c, "vx"), FloatArgumentType.getFloat(c, "vy")))))))));
    }

    private static int objective(Collection<ServerPlayer> ps, String text) {
        lastText = text;
        if (text.isEmpty()) lastWp = null;
        send(ps);
        return ps.size();
    }

    private static int waypoint(Collection<ServerPlayer> ps, Vec3 wp) {
        lastWp = wp;
        send(ps);
        return ps.size();
    }

    private static void send(Collection<ServerPlayer> ps) {
        Net.Objective o = lastWp == null ? new Net.Objective(lastText, false, 0, 0, 0)
                : new Net.Objective(lastText, true, lastWp.x, lastWp.y, lastWp.z);
        for (ServerPlayer p : ps) Net.to(p, o);
    }

    private static int anim(Collection<? extends Entity> es, String name) {
        String a = name.equals("stop") ? "" : name;
        for (Entity e : es) Net.around(e, new Net.Anim(e.getId(), a));
        return es.size();
    }

    /** 玩家重新連線時補送目前的目標。 */
    static void resend(ServerPlayer p) { send(List.of(p)); }

    // ---- 軌跡測量 ----
    private record Trace(Entity e, int[] age) {}

    private static final List<Trace> TRACES = new ArrayList<>();

    private static int trace(CommandSourceStack src, ResourceLocation type, Vec3 pos, float vx, float vy) {
        EntityType<?> t = ForgeRegistries.ENTITY_TYPES.getValue(type);
        ServerLevel level = src.getLevel();
        Entity e = t == null ? null : t.create(level);
        if (e == null) { src.sendFailure(Component.literal("unknown entity " + type)); return 0; }
        e.moveTo(pos.x, pos.y, pos.z, 0, 0);
        net.minecraft.nbt.CompoundTag nbt = e.saveWithoutId(new net.minecraft.nbt.CompoundTag());
        nbt.putBoolean("CanUpdate", true);   // Superb Warfare 的拋射物沒有這個旗標不會動
        e.load(nbt);
        e.setDeltaMovement(vx, vy, 0);
        level.addFreshEntity(e);
        TRACES.add(new Trace(e, new int[]{0}));
        LOG.info("[lntrace] start {} pos {} v {} {}", type, pos, vx, vy);
        return 1;
    }

    static void onServerTick(TickEvent.ServerTickEvent e) {
        if (e.phase != TickEvent.Phase.END || TRACES.isEmpty()) return;
        TRACES.removeIf(t -> {
            int a = ++t.age[0];
            Vec3 p = t.e.position(), v = t.e.getDeltaMovement();
            LOG.info("[lntrace] t={} x={} y={} vx={} vy={} alive={}", a, String.format("%.4f", p.x), String.format("%.4f", p.y),
                    String.format("%.5f", v.x), String.format("%.5f", v.y), t.e.isAlive());
            return !t.e.isAlive() || a >= 40;
        });
    }
}
