package dev.longnight.lnai;

import java.util.EnumSet;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.goal.Goal;

/** 有目標但被牆擋住看不到：繞路走到看得見的位置（例如從門口進屋），而不是隔著牆發呆。 */
class ChaseGoal extends Goal {
    private final PathfinderMob mob;
    private int blind;
    private int repath;

    ChaseGoal(PathfinderMob mob) {
        this.mob = mob;
        setFlags(EnumSet.of(Flag.MOVE));
    }

    private boolean wants() {
        LivingEntity t = mob.getTarget();
        if (t == null || !t.isAlive() || !Orders.hostile(mob, t)) {
            blind = 0;
            return false;
        }
        if (mob.hasLineOfSight(t)) {
            blind = 0;
            return false;
        }
        return ++blind > 30;      // 看不到超過 1.5 秒才繞路
    }

    @Override
    public boolean canUse() {
        return wants();
    }

    @Override
    public boolean canContinueToUse() {
        LivingEntity t = mob.getTarget();
        return t != null && t.isAlive() && !mob.hasLineOfSight(t);
    }

    @Override
    public void start() {
        repath = 0;
    }

    @Override
    public void tick() {
        if (--repath > 0) return;
        repath = 15;
        LivingEntity t = mob.getTarget();
        if (t != null) mob.getNavigation().moveTo(t, Orders.speed(mob) * 1.15);
    }

    @Override
    public void stop() {
        blind = 0;
        mob.getNavigation().stop();
    }
}
