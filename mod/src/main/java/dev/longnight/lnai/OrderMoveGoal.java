package dev.longnight.lnai;

import java.util.EnumSet;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.phys.Vec3;

/** 沒有交戰時，往 ForgeData.ln_wp 指定的位置推進；依 ln_slot 錯開站位，看起來像隊形。 */
class OrderMoveGoal extends Goal {
    private final PathfinderMob mob;
    private int repath;

    OrderMoveGoal(PathfinderMob mob) {
        this.mob = mob;
        setFlags(EnumSet.of(Flag.MOVE));
    }

    private Vec3 point() {
        CompoundTag d = Orders.data(mob);
        if (!d.contains("ln_wp")) return null;
        int[] a = d.getIntArray("ln_wp");
        if (a.length < 3) return null;
        int slot = d.getInt("ln_slot");
        double ang = slot * 2.4;               // 黃金角錯開
        double r = slot == 0 ? 0 : 1.5 + (slot % 3);
        return new Vec3(a[0] + 0.5 + Math.cos(ang) * r, a[1], a[2] + 0.5 + Math.sin(ang) * r);
    }

    private double radius() {
        CompoundTag d = Orders.data(mob);
        return d.contains("ln_wpr") ? d.getInt("ln_wpr") : 3;
    }

    private boolean wants() {
        Vec3 p = point();
        if (p == null || Orders.engaged(mob, 24)) return false;
        return mob.position().distanceToSqr(p) > radius() * radius();
    }

    @Override
    public boolean canUse() {
        return wants();
    }

    @Override
    public boolean canContinueToUse() {
        return wants();
    }

    @Override
    public void start() {
        repath = 0;
    }

    @Override
    public void tick() {
        if (--repath > 0) return;
        repath = 20;
        Vec3 p = point();
        if (p != null) {
            double dist = mob.position().distanceTo(p);
            mob.getNavigation().moveTo(p.x, p.y, p.z, Orders.speed(mob) * (dist > 16 ? 1.25 : 1.0));
        }
    }

    @Override
    public void stop() {
        mob.getNavigation().stop();
    }
}
