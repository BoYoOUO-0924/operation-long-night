package dev.longnight.lnai;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import net.minecraft.network.protocol.game.ClientboundSetCarriedItemPacket;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/**
 * 快速近戰：拿槍時按一下近戰鍵 → 切到 3 號近戰武器、立刻揮一刀（全力傷害）→ 0.5 秒後切回原本的欄位。
 * 由伺服器判定命中，不受原版「剛換武器攻擊力很低」的限制。
 */
final class Melee {
    private Melee() {}

    static final int SLOT = 2, BACK_TICKS = 10, COOLDOWN = 14;
    static final double REACH = 3.0;

    private record Pending(int restore, int[] left) {}

    private static final Map<UUID, Pending> BACK = new HashMap<>();
    private static final Map<UUID, Long> LAST = new HashMap<>();

    static void quick(ServerPlayer p, int prevSlot) {
        if (p.isPassenger()) return;   // 在載具裡 V 是載具的按鍵（熱焰彈）
        long now = p.level().getGameTime();
        Long last = LAST.get(p.getUUID());
        if (last != null && now - last < COOLDOWN) return;
        if (!Loadout.equip(p.getInventory(), SLOT, Loadout::isMelee)) { Loadout.tell(p, "沒有近戰武器"); return; }
        LAST.put(p.getUUID(), now);

        select(p, SLOT);
        ItemStack knife = p.getInventory().getItem(SLOT);
        p.swing(InteractionHand.MAIN_HAND, true);
        p.level().playSound(null, p.blockPosition(), SoundEvents.PLAYER_ATTACK_SWEEP, SoundSource.PLAYERS, 0.7f, 1.3f);

        LivingEntity target = aim(p);
        if (target != null) {
            float dmg = damage(knife, target);
            if (target.hurt(p.damageSources().playerAttack(p), dmg)) {
                float yaw = p.getYRot() * Mth.DEG_TO_RAD;
                target.knockback(0.4, Mth.sin(yaw), -Mth.cos(yaw));
                knife.hurtEnemy(target, p);
                p.level().playSound(null, target.blockPosition(), SoundEvents.PLAYER_ATTACK_STRONG, SoundSource.PLAYERS, 1f, 1f);
            }
        }
        // 原本就拿著近戰武器（或在 4、5 欄以外）就不用切回
        int restore = prevSlot >= 0 && prevSlot <= Gear.LAST_SLOT && prevSlot != SLOT ? prevSlot : -1;
        if (restore >= 0) BACK.put(p.getUUID(), new Pending(restore, new int[]{BACK_TICKS}));
    }

    /** 每 tick 由 Heal.onTick 呼叫：時間到就切回原本的武器；玩家自己換過欄位就不管。 */
    static void tick(ServerPlayer p) {
        Pending b = BACK.get(p.getUUID());
        if (b == null || --b.left[0] > 0) return;
        BACK.remove(p.getUUID());
        if (p.isAlive() && p.getInventory().selected == SLOT) select(p, b.restore);
    }

    private static void select(ServerPlayer p, int slot) {
        p.getInventory().selected = slot;
        p.connection.send(new ClientboundSetCarriedItemPacket(slot));
    }

    private static LivingEntity aim(ServerPlayer p) {
        Vec3 eye = p.getEyePosition(), look = p.getViewVector(1f);
        double reach = REACH;
        HitResult block = p.pick(REACH, 1f, false);
        if (block.getType() != HitResult.Type.MISS) reach = block.getLocation().distanceTo(eye);
        Vec3 end = eye.add(look.scale(reach));
        AABB box = p.getBoundingBox().expandTowards(look.scale(reach)).inflate(1.0);
        EntityHitResult hit = ProjectileUtil.getEntityHitResult(p.level(), p, eye, end, box,
                e -> e instanceof LivingEntity && e.isAlive() && !e.isSpectator() && e.isPickable(), 0.3f);
        Entity e = hit == null ? null : hit.getEntity();
        return e instanceof LivingEntity le ? le : null;
    }

    /** 武器本身的攻擊力（不看攻擊冷卻）：1 ＋ 物品加成 ＋ 附魔。 */
    private static float damage(ItemStack s, LivingEntity target) {
        double d = 1.0;
        for (AttributeModifier m : s.getAttributeModifiers(EquipmentSlot.MAINHAND).get(Attributes.ATTACK_DAMAGE))
            if (m.getOperation() == AttributeModifier.Operation.ADDITION) d += m.getAmount();
        return (float) d + EnchantmentHelper.getDamageBonus(s, target.getMobType());
    }
}
