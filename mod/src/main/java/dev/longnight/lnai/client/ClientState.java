package dev.longnight.lnai.client;

import java.util.ArrayDeque;
import java.util.Deque;
import dev.longnight.lnai.Gear;
import dev.longnight.lnai.Net;
import net.minecraft.client.Minecraft;
import net.minecraft.world.phys.Vec3;

/** 玩家端的介面狀態（只活在這台電腦上）。 */
public final class ClientState {
    private ClientState() {}

    /** 玩家選好的投擲物（長按 4 的輪盤會改它）。 */
    public static Gear.Grenade grenade = Gear.Grenade.M67;

    // 治療進度
    public static Gear.Med healMed = null;
    public static int healTotal = 0;
    public static long healStart = 0;

    // 投擲落點距離（-1 = 沒有落點）
    public static double arcDist = -1;
    public static long arcTime = -100;

    // 目標
    public static String objective = "";
    public static Vec3 waypoint = null;

    // 擊殺
    public record Feed(String killer, String role, boolean mine, long time) {}

    public static final Deque<Feed> FEED = new ArrayDeque<>();
    public static String bigKill = "";
    public static long bigKillTime = -100;

    static long now() {
        Minecraft mc = Minecraft.getInstance();
        return mc.level == null ? 0 : mc.level.getGameTime();
    }

    public static void onHeal(Net.HealSync m) {
        if (m.med() < 0) {
            healMed = null;
            Minecraft mc = Minecraft.getInstance();
            if (m.restore() >= 0 && m.restore() <= Gear.LAST_SLOT && mc.player != null) mc.player.getInventory().selected = m.restore();
        } else {
            healMed = Gear.Med.values()[m.med()];
            healTotal = m.total();
            healStart = now();
        }
    }

    public static void onKill(Net.Kill k) {
        FEED.addFirst(new Feed(k.killer(), k.role(), k.mine(), now()));
        while (FEED.size() > 5) FEED.removeLast();
        if (k.mine()) { bigKill = "✕ 擊殺 " + k.role(); bigKillTime = now(); }
    }

    public static void onObjective(Net.Objective o) {
        objective = o.text();
        waypoint = o.hasWp() ? new Vec3(o.x(), o.y(), o.z()) : null;
    }
}
