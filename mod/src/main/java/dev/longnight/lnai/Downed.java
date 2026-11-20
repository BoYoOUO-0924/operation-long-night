package dev.longnight.lnai;

import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ClientboundSetCarriedItemPacket;
import net.minecraft.network.protocol.game.ClientboundSetTitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetSubtitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetTitlesAnimationPacket;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.level.GameType;
import net.minecraft.world.scores.Objective;
import net.minecraft.world.scores.Scoreboard;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingAttackEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.server.ServerLifecycleHooks;

/**
 * 倒地與救援。
 * <ul>
 *   <li>關卡進行中（#stage ln ≥ 1）、冒險模式的玩家血量歸零時不會死，而是倒地：趴著、只能用手槍。</li>
 *   <li>倒地可撐 30 秒；同一階段第 2 次 20 秒、之後 10 秒。倒地時中彈會扣 3 秒。被救的時候計時暫停。</li>
 *   <li>隊友靠近按住 F 4 秒救起，起來時 30% 血。</li>
 *   <li>倒地 8 秒都沒有玩家在救，最近的 NPC 隊友（白鴉、戰車、狐狸）會跑過來，花 8 秒救起。</li>
 *   <li>時間到沒人救就陣亡（變成旁觀），進入下一個階段時在隊友身邊復活。</li>
 *   <li>全隊都倒地或陣亡：全員復活，執行資料包的 ln:wipe 從本階段重來。</li>
 * </ul>
 */
public final class Downed {
    private Downed() {}

    static final int[] BLEED = {600, 400, 200};
    static final int REVIVE_TICKS = 80, NPC_REVIVE_TICKS = 160, NPC_CALL_AFTER = 160, NPC_GIVE_UP = 400, HIT_PENALTY = 60;
    static final double REVIVE_RANGE = 2.6;
    static final int PISTOL_SLOT = 1;

    static final class State {
        int bleed, bleedMax, age;
        UUID reviver;            // 正在救的玩家
        Mob npc;                 // 正在趕來／正在救的 NPC
        int npcAge;              // NPC 出發後經過幾 tick
        boolean npcWorking;      // NPC 已經到了、正在救
        int progress, progressMax;
    }

    static final Map<UUID, State> DOWN = new HashMap<>();
    /** 陣亡等待復活的玩家 */
    static final Set<UUID> DEAD = new HashSet<>();
    /** 本階段已經倒地幾次 */
    static final Map<UUID, Integer> DOWNS = new HashMap<>();
    private static int lastStage = -1;

    public static boolean isDowned(ServerPlayer p) { return DOWN.containsKey(p.getUUID()); }

    static boolean isDead(ServerPlayer p) { return DEAD.contains(p.getUUID()); }

    static State state(ServerPlayer p) { return DOWN.get(p.getUUID()); }

    // ---------------------------------------------------------------- 事件
    /** 優先序最高：取消死亡，改成倒地（擊殺通報那邊就不會收到） */
    static void onDeath(LivingDeathEvent e) {
        if (!(e.getEntity() instanceof ServerPlayer p)) return;
        if (!eligible(p) || e.getSource().is(DamageTypeTags.BYPASSES_INVULNERABILITY)) return;
        if (isDowned(p)) { e.setCanceled(true); p.setHealth(1); return; }
        e.setCanceled(true);
        goDown(p);
    }

    /** 倒地的人不再扣血，但每中一下少 3 秒 */
    static void onAttack(LivingAttackEvent e) {
        if (!(e.getEntity() instanceof ServerPlayer p) || !isDowned(p)) return;
        DamageSource s = e.getSource();
        if (s.is(DamageTypeTags.BYPASSES_INVULNERABILITY)) return;
        e.setCanceled(true);
        if (s.getEntity() != null || s.getDirectEntity() != null) {
            State st = state(p);
            st.bleed = Math.max(0, st.bleed - HIT_PENALTY);
        }
    }

    private static boolean eligible(ServerPlayer p) {
        return p.gameMode.getGameModeForPlayer() == GameType.ADVENTURE && stage(p.server) >= 1;
    }

    static int stage(MinecraftServer s) {
        Scoreboard sb = s.getScoreboard();
        Objective o = sb.getObjective("ln");
        if (o == null || !sb.hasPlayerScore("#stage", o)) return 0;
        return sb.getOrCreatePlayerScore("#stage", o).getScore();
    }

    private static void goDown(ServerPlayer p) {
        int n = DOWNS.merge(p.getUUID(), 1, Integer::sum);
        State st = new State();
        st.bleed = st.bleedMax = BLEED[Math.min(n - 1, BLEED.length - 1)];
        DOWN.put(p.getUUID(), st);
        p.setHealth(1);
        p.clearFire();
        p.removeAllEffects();
        p.stopUsingItem();
        Heal.cancel(p);
        selectPistol(p);
        Net.to(p, new Net.DownedSync(true));
        p.level().playSound(null, p.blockPosition(), net.minecraft.sounds.SoundEvents.PLAYER_HURT, net.minecraft.sounds.SoundSource.PLAYERS, 1, 0.6f);
        for (ServerPlayer o : p.server.getPlayerList().getPlayers())
            if (o != p) Net.to(o, new Net.Say("", 0xC8604F, p.getGameProfile().getName() + " 倒地了！", 60));
    }

    private static void selectPistol(ServerPlayer p) {
        if (p.getInventory().selected != PISTOL_SLOT) {
            p.getInventory().selected = PISTOL_SLOT;
            p.connection.send(new ClientboundSetCarriedItemPacket(PISTOL_SLOT));
        }
    }

    private static void standUp(ServerPlayer p, float frac) {
        State st = DOWN.remove(p.getUUID());
        if (st != null && st.npc != null) releaseNpc(st.npc);
        p.setHealth(Math.max(1, p.getMaxHealth() * frac));
        p.invulnerableTime = 40;   // 剛站起來的 2 秒不會馬上又倒
        Net.to(p, new Net.DownedSync(false));
    }

    private static void releaseNpc(Mob m) {
        if (m.isAlive()) m.setNoAi(false);
        m.getNavigation().stop();
    }

    // ---------------------------------------------------------------- 救援（玩家）
    /** 玩家按住／放開 F。target = 倒地玩家的實體編號 */
    static void onRevive(ServerPlayer reviver, int target, boolean hold) {
        for (Map.Entry<UUID, State> en : DOWN.entrySet()) {
            State st = en.getValue();
            if (reviver.getUUID().equals(st.reviver) && (!hold || reviver.level().getEntity(target) == null
                    || !reviver.level().getEntity(target).getUUID().equals(en.getKey()))) {
                st.reviver = null;
                st.progress = 0;
            }
        }
        if (!hold || isDowned(reviver) || isDead(reviver)) return;
        if (!(reviver.level().getEntity(target) instanceof ServerPlayer t)) return;
        State st = state(t);
        if (st == null || st.reviver != null || reviver.distanceTo(t) > REVIVE_RANGE) return;
        st.reviver = reviver.getUUID();
        st.progress = 0;
        st.progressMax = REVIVE_TICKS;
        if (st.npc != null) { releaseNpc(st.npc); st.npc = null; st.npcWorking = false; }
    }

    // ---------------------------------------------------------------- 每 tick
    static void onTick(TickEvent.ServerTickEvent e) {
        if (e.phase != TickEvent.Phase.END) return;
        MinecraftServer s = ServerLifecycleHooks.getCurrentServer();
        if (s == null) return;
        int stage = stage(s);
        if (stage != lastStage) {
            if (lastStage != -1) onStageChange(s, stage);
            lastStage = stage;
        }
        if (stage < 1 && !DOWN.isEmpty()) {   // 關卡結束或中止：全部站起來
            for (ServerPlayer p : s.getPlayerList().getPlayers()) if (isDowned(p)) standUp(p, 1);
            DOWN.clear();
        }
        for (ServerPlayer p : List.copyOf(s.getPlayerList().getPlayers())) {
            State st = state(p);
            if (st == null) continue;
            st.age++;
            p.setHealth(Math.max(1, Math.min(p.getHealth(), 1)));
            selectPistol(p);
            if (p.tickCount % 20 == 0) p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 30, 1, false, false));
            // 玩家救援
            ServerPlayer rv = st.reviver == null ? null : s.getPlayerList().getPlayer(st.reviver);
            if (rv != null && (rv.distanceTo(p) > REVIVE_RANGE + 0.6 || isDowned(rv) || !rv.isAlive())) { st.reviver = null; st.progress = 0; rv = null; }
            if (rv != null) {
                if (++st.progress >= st.progressMax) { standUp(p, 0.3f); continue; }
            } else {
                tickNpc(s, p, st);
                if (st.npcWorking) {
                    if (++st.progress >= st.progressMax) { standUp(p, 0.3f); continue; }
                } else if (--st.bleed <= 0) {
                    die(p);
                    continue;
                }
            }
        }
        checkWipe(s);
    }

    private static void tickNpc(MinecraftServer s, ServerPlayer p, State st) {
        if (st.npc == null) {
            if (st.age < NPC_CALL_AFTER) return;
            st.npc = nearestAlly(p);
            st.npcAge = 0;
            if (st.npc == null) return;
            String n = st.npc.hasCustomName() ? st.npc.getCustomName().getString() : "隊友";
            Net.to(p, new Net.Say(n, 0xE4E2DA, "撐住！我過來了！", 60));
        }
        Mob m = st.npc;
        if (!m.isAlive()) { st.npc = null; st.npcWorking = false; st.progress = 0; return; }
        st.npcAge++;
        double d = m.distanceTo(p);
        if (!st.npcWorking) {
            if (d <= 1.8 || st.npcAge > NPC_GIVE_UP) {
                if (d > 1.8) m.teleportTo(p.getX() + 1, p.getY(), p.getZ());   // 路走不通：直接到旁邊，避免單人卡死
                m.getNavigation().stop();
                m.setNoAi(true);
                st.npcWorking = true;
                st.progress = 0;
                st.progressMax = NPC_REVIVE_TICKS;
            } else if (st.npcAge % 5 == 1) {
                m.getNavigation().moveTo(p, 1.35);
            }
        } else {
            m.getLookControl().setLookAt(p);
            m.setYRot(yawTo(m, p));
            m.setYHeadRot(m.getYRot());
        }
    }

    private static float yawTo(Mob m, ServerPlayer p) {
        return (float) Math.toDegrees(Math.atan2(-(p.getX() - m.getX()), p.getZ() - m.getZ()));
    }

    private static Mob nearestAlly(ServerPlayer p) {
        Mob best = null;
        double bd = 1e9;
        Set<Mob> busy = new HashSet<>();
        for (State o : DOWN.values()) if (o.npc != null) busy.add(o.npc);
        for (var en : ((ServerLevel) p.level()).getAllEntities())
            if (en instanceof Mob m && m.isAlive() && m.getTags().contains("ln_ally") && !m.getTags().contains("ln_officer") && !busy.contains(m)) {
                double d = m.distanceToSqr(p);
                if (d < bd) { bd = d; best = m; }
            }
        return best;
    }

    private static boolean nearestAllyAny(ServerPlayer p) {
        for (var en : ((ServerLevel) p.level()).getAllEntities())
            if (en instanceof Mob m && m.isAlive() && m.getTags().contains("ln_ally") && !m.getTags().contains("ln_officer")) return true;
        return false;
    }

    private static void die(ServerPlayer p) {
        State st = DOWN.remove(p.getUUID());
        if (st != null && st.npc != null) releaseNpc(st.npc);
        DEAD.add(p.getUUID());
        Net.to(p, new Net.DownedSync(false));
        p.setHealth(p.getMaxHealth());
        p.setGameMode(GameType.SPECTATOR);
        title(p, "陣亡", "進入下一個階段時會在隊友身邊復活");
        for (ServerPlayer o : p.server.getPlayerList().getPlayers())
            if (o != p) Net.to(o, new Net.Say("", 0xC8604F, p.getGameProfile().getName() + " 陣亡了", 80));
    }

    private static void onStageChange(MinecraftServer s, int stage) {
        DOWNS.clear();
        if (DEAD.isEmpty()) return;
        List<ServerPlayer> alive = s.getPlayerList().getPlayers().stream()
                .filter(p -> !isDead(p) && !isDowned(p) && p.gameMode.getGameModeForPlayer() == GameType.ADVENTURE).toList();
        for (UUID id : List.copyOf(DEAD)) {
            ServerPlayer p = s.getPlayerList().getPlayer(id);
            DEAD.remove(id);
            if (p == null) continue;
            if (stage >= 1 && !alive.isEmpty()) {
                ServerPlayer to = alive.get(p.getRandom().nextInt(alive.size()));
                p.teleportTo((ServerLevel) to.level(), to.getX(), to.getY(), to.getZ(), to.getYRot(), 0);
            }
            p.setGameMode(stage >= 1 ? GameType.ADVENTURE : GameType.CREATIVE);
            p.setHealth(p.getMaxHealth());
            title(p, "歸隊", "");
        }
    }

    private static void checkWipe(MinecraftServer s) {
        if (DOWN.isEmpty() && DEAD.isEmpty()) return;
        // 有 NPC 隊友還能來救的話，倒地不算出局；只有全部陣亡（或沒有 NPC 可救）才算全隊覆沒
        boolean npcHelp = false;
        for (ServerPlayer p : s.getPlayerList().getPlayers()) { if (nearestAllyAny(p)) { npcHelp = true; break; } }
        int participants = 0, out = 0;
        for (ServerPlayer p : s.getPlayerList().getPlayers()) {
            boolean in = p.gameMode.getGameModeForPlayer() == GameType.ADVENTURE || isDead(p);
            if (!in) continue;
            participants++;
            if (isDead(p) || (isDowned(p) && !npcHelp)) out++;
        }
        if (participants == 0 || out < participants) return;
        // 全隊覆沒：全員復活，從本階段重來
        for (ServerPlayer p : s.getPlayerList().getPlayers()) {
            boolean was = isDowned(p) || isDead(p);
            if (!was) continue;
            if (isDowned(p)) standUp(p, 1);
            DEAD.remove(p.getUUID());
            p.setGameMode(GameType.ADVENTURE);
            p.setHealth(p.getMaxHealth());
            BlockPos rp = p.getRespawnPosition();
            if (rp != null) p.teleportTo(s.getLevel(p.getRespawnDimension()), rp.getX() + 0.5, rp.getY(), rp.getZ() + 0.5, p.getYRot(), 0);
            p.addEffect(new MobEffectInstance(MobEffects.BLINDNESS, 40, 0, false, false));
            title(p, "全隊陣亡", "從本階段重新開始");
        }
        DOWN.clear();
        DEAD.clear();
        DOWNS.clear();
        s.getCommands().performPrefixedCommand(s.createCommandSourceStack().withSuppressedOutput().withPermission(2), "function ln:wipe");
    }

    private static void title(ServerPlayer p, String t, String sub) {
        p.connection.send(new ClientboundSetTitlesAnimationPacket(10, 50, 20));
        p.connection.send(new ClientboundSetSubtitleTextPacket(Component.literal(sub)));
        p.connection.send(new ClientboundSetTitleTextPacket(Component.literal(t)));
    }

    /** 給 TeamSync：目前的倒地資訊 */
    static float bleedFrac(ServerPlayer p) {
        State st = state(p);
        return st == null ? 0 : st.bleed / (float) st.bleedMax;
    }

    static float progress(ServerPlayer p) {
        State st = state(p);
        return st == null || st.progressMax == 0 || (st.reviver == null && !st.npcWorking) ? 0 : st.progress / (float) st.progressMax;
    }

    static int bleedSeconds(ServerPlayer p) {
        State st = state(p);
        return st == null ? 0 : (st.bleed + 19) / 20;
    }

    static String helper(ServerPlayer p) {
        State st = state(p);
        if (st == null) return "";
        if (st.reviver != null) {
            ServerPlayer r = p.server.getPlayerList().getPlayer(st.reviver);
            return r == null ? "" : r.getGameProfile().getName();
        }
        return st.npc != null && st.npc.hasCustomName() ? st.npc.getCustomName().getString() : "";
    }
}
