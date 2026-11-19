package dev.longnight.lnai;

import java.util.EnumSet;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.phys.AABB;

/**
 * 選目標：
 *  1. 小隊共享：隊友正在打誰，我也打誰（小隊一起轉向、一起壓上去）
 *  2. 主動搜索：ln_hunt 範圍內「知道」最近的敵人在哪，不需要看見（會繞路找過去）
 */
class SquadTargetGoal extends Goal {
    private final PathfinderMob mob;
    private LivingEntity chosen;
    private int cooldown;

    SquadTargetGoal(PathfinderMob mob) {
        this.mob = mob;
        setFlags(EnumSet.of(Flag.TARGET));
    }

    @Override
    public boolean canUse() {
        if (--cooldown > 0) return false;
        cooldown = 10;
        LivingEntity cur = mob.getTarget();
        if (cur != null && cur.isAlive() && Orders.hostile(mob, cur)) return false;
        chosen = pick();
        return chosen != null;
    }

    private LivingEntity pick() {
        String squad = Orders.squad(mob);
        AABB box = mob.getBoundingBox().inflate(40);
        if (!squad.isEmpty()) {
            for (PathfinderMob mate : mob.level().getEntitiesOfClass(PathfinderMob.class, box,
                    e -> e != mob && squad.equals(Orders.squad(e)))) {
                LivingEntity t = mate.getTarget();
                if (t != null && Orders.hostile(mob, t)) return t;
            }
        }
        int hunt = Orders.data(mob).getInt("ln_hunt");
        if (hunt <= 0) return null;
        LivingEntity best = null;
        double bd = (double) hunt * hunt;
        for (LivingEntity e : mob.level().getEntitiesOfClass(LivingEntity.class, mob.getBoundingBox().inflate(hunt),
                e -> Orders.hostile(mob, e))) {
            double d = e.distanceToSqr(mob);
            if (d < bd) {
                bd = d;
                best = e;
            }
        }
        return best;
    }

    @Override
    public void start() {
        mob.setTarget(chosen);
    }

    @Override
    public boolean canContinueToUse() {
        return false;
    }
}
