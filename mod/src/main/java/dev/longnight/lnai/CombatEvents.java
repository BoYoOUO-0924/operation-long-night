package dev.longnight.lnai;

import java.util.Map;
import net.minecraft.ChatFormatting;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraftforge.event.entity.living.LivingAttackEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;

/** 友軍不互傷，以及擊殺通報。 */
final class CombatEvents {
    private CombatEvents() {}

    private static final Map<String, String> ROLE = Map.of(
            "red_assault", "突擊兵", "red_support", "機槍手", "red_sniper", "狙擊手", "red_cqb", "近戰兵");

    /** 找出真正開槍的人（子彈的主人）。 */
    static Entity shooter(Entity src, Entity direct) {
        if (src != null) return src;
        if (direct instanceof Projectile p) return p.getOwner();
        return direct;
    }

    static void onAttack(LivingAttackEvent e) {
        LivingEntity victim = e.getEntity();
        if (victim.level().isClientSide()) return;
        Entity s = shooter(e.getSource().getEntity(), e.getSource().getDirectEntity());
        if (!(s instanceof LivingEntity attacker) || attacker == victim) return;
        String a = Orders.side(attacker), v = Orders.side(victim);
        if (!a.isEmpty() && a.equals(v)) e.setCanceled(true);       // 同陣營：子彈穿過、不受傷
    }

    static void onDeath(LivingDeathEvent e) {
        LivingEntity victim = e.getEntity();
        if (!(victim.level() instanceof ServerLevel level)) return;
        if (!"red".equals(Orders.side(victim))) return;
        Entity s = shooter(e.getSource().getEntity(), e.getSource().getDirectEntity());

        CompoundTag tag = new CompoundTag();
        victim.saveWithoutId(tag);
        String role = ROLE.getOrDefault(tag.getString("template"), "敵兵");

        MutableComponent killer;
        if (s instanceof ServerPlayer p) {
            killer = Component.literal(p.getGameProfile().getName()).withStyle(ChatFormatting.AQUA, ChatFormatting.BOLD);
            p.displayClientMessage(Component.literal("✕ 擊殺 " + role).withStyle(ChatFormatting.RED, ChatFormatting.BOLD), true);
            level.playSound(null, p.blockPosition(), SoundEvents.EXPERIENCE_ORB_PICKUP, SoundSource.PLAYERS, 0.7f, 0.6f);
        } else if (s != null && s.hasCustomName()) {
            killer = s.getCustomName().copy().withStyle(ChatFormatting.BOLD);
        } else if (s instanceof LivingEntity le && "blue".equals(Orders.side(le))) {
            killer = Component.literal("友軍").withStyle(ChatFormatting.AQUA);
        } else {
            return;
        }
        Component msg = Component.literal("⌖ ").withStyle(ChatFormatting.DARK_GRAY)
                .append(killer)
                .append(Component.literal(" 擊倒了 ").withStyle(ChatFormatting.GRAY))
                .append(Component.literal(role).withStyle(ChatFormatting.RED));
        for (ServerPlayer p : level.players()) p.sendSystemMessage(msg);
    }
}
