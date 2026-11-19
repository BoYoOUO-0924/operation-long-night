package dev.longnight.lnai;

import java.util.EnumSet;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;

/** 隊友：沒有交戰時跟在最近的玩家附近（依 ln_slot 錯開，站在玩家側後方）；離太遠就傳送歸隊。 */
class FollowPlayerGoal extends Goal {
    private final PathfinderMob mob;
    private Player leader;
    private int repath;

    FollowPlayerGoal(PathfinderMob mob) {
        this.mob = mob;
        setFlags(EnumSet.of(Flag.MOVE));
    }

    private boolean enabled() {
        return Orders.data(mob).getBoolean("ln_follow") && !Orders.data(mob).contains("ln_wp");
    }

    private Player findLeader() {
        Player best = null;
        double bd = 96 * 96;
        for (Player p : mob.level().players()) {
            if (p.isSpectator() || p.isCreative() || !p.isAlive()) continue;
            double d = p.distanceToSqr(mob);
            if (d < bd) {
                bd = d;
                best = p;
            }
        }
        return best;
    }

    private Vec3 spot() {
        int slot = Orders.data(mob).getInt("ln_slot");
        Vec3 look = leader.getLookAngle().multiply(1, 0, 1).normalize();
        Vec3 side = new Vec3(-look.z, 0, look.x);
        double s = (slot % 2 == 0 ? 1 : -1) * (2 + slot);
        return leader.position().subtract(look.scale(2.5)).add(side.scale(s * 0.8));
    }

    @Override
    public boolean canUse() {
        if (!enabled() || Orders.engaged(mob, 20)) return false;
        leader = findLeader();
        return leader != null && mob.distanceToSqr(leader) > 5 * 5;
    }

    @Override
    public boolean canContinueToUse() {
        return enabled() && leader != null && leader.isAlive() && !Orders.engaged(mob, 20)
                && mob.distanceToSqr(leader) > 3 * 3;
    }

    @Override
    public void start() {
        repath = 0;
    }

    @Override
    public void tick() {
        mob.getLookControl().setLookAt(leader, 30, 30);
        if (--repath > 0) return;
        repath = 10;
        double d = mob.distanceTo(leader);
        if (d > 40 && !mob.hasLineOfSight(leader)) {      // 跟丟了：傳送到玩家身後
            Vec3 s = spot();
            mob.teleportTo(s.x, leader.getY(), s.z);
            mob.getNavigation().stop();
            return;
        }
        Vec3 s = spot();
        mob.getNavigation().moveTo(s.x, leader.getY(), s.z, Orders.speed(mob) * (d > 10 ? 1.35 : 1.0));
    }

    @Override
    public void stop() {
        mob.getNavigation().stop();
    }
}
