package dev.longnight.lnai;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.player.Player;

/** 讀取 ForgeData 命令與共用判斷。 */
final class Orders {
    private Orders() {}

    static CompoundTag data(LivingEntity e) {
        return e.getPersistentData();
    }

    static String side(LivingEntity e) {
        if (e instanceof Player) return "blue";
        return data(e).getString("ln_side");
    }

    static String squad(LivingEntity e) {
        return data(e).getString("ln_squad");
    }

    static float speed(PathfinderMob m) {
        CompoundTag d = data(m);
        return d.contains("ln_speed") ? d.getFloat("ln_speed") : 1.0f;
    }

    /** a 是否應該攻擊 b。 */
    static boolean hostile(LivingEntity a, LivingEntity b) {
        if (b == null || !b.isAlive() || a == b) return false;
        if (b instanceof Player p && (p.isCreative() || p.isSpectator())) return false;
        String sa = side(a), sb = side(b);
        if (sa.isEmpty() || sb.isEmpty()) return false;
        return !sa.equals(sb);
    }

    /** 正在跟看得見、夠近的敵人交戰中（交戰時讓原本的射擊 AI 主導）。 */
    static boolean engaged(PathfinderMob m, double range) {
        LivingEntity t = m.getTarget();
        return t != null && t.isAlive() && m.distanceToSqr(t) < range * range && m.hasLineOfSight(t);
    }
}
