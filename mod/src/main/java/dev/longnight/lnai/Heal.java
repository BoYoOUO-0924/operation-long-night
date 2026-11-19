package dev.longnight.lnai;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraftforge.event.TickEvent;

/** 伺服器端治療流程：拿出醫療用品 → 計時 → 補血、扣物品 → 切回原本的武器。換欄位就中斷。 */
final class Heal {
    private Heal() {}

    private record Job(Gear.Med med, int restore, int[] left) {}

    private static final Map<UUID, Job> JOBS = new HashMap<>();
    private static final UUID SLOW = UUID.fromString("6b1f0c1e-6d0a-4b47-9a51-5a3e1c0d7f11");

    static void start(ServerPlayer p, Gear.Med med, int restore) {
        if (p.getHealth() >= p.getMaxHealth() && med != Gear.Med.PAINKILLER) {
            Loadout.tell(p, "生命值已滿");
            Net.to(p, new Net.HealSync(-1, 0, restore));
            return;
        }
        if (!Loadout.equip(p.getInventory(), Gear.SLOT_MED, med::is)) return;
        p.getInventory().selected = Gear.SLOT_MED;
        if (restore == Gear.SLOT_MED) restore = 0;
        JOBS.put(p.getUUID(), new Job(med, restore, new int[]{med.ticks}));
        slow(p, med == Gear.Med.MEDKIT ? -0.5 : -0.25);
        p.level().playSound(null, p.blockPosition(), SoundEvents.ARMOR_EQUIP_LEATHER, SoundSource.PLAYERS, 0.8f, 1.2f);
        Net.to(p, new Net.HealSync(med.ordinal(), med.ticks, -1));
    }

    static void onTick(TickEvent.PlayerTickEvent e) {
        if (e.phase != TickEvent.Phase.END || !(e.player instanceof ServerPlayer p)) return;
        if (p.tickCount % 10 == 0) Loadout.tidy(p);
        Job j = JOBS.get(p.getUUID());
        if (j == null) return;
        if (!p.isAlive() || p.getInventory().selected != Gear.SLOT_MED || !j.med.is(p.getInventory().getItem(Gear.SLOT_MED))) {
            stop(p, -1);
            Loadout.tell(p, "治療中斷");
            return;
        }
        if (--j.left[0] > 0) return;
        p.getInventory().getItem(Gear.SLOT_MED).shrink(1);
        p.heal(j.med.heal);
        if (j.med.regenTicks > 0) p.addEffect(new MobEffectInstance(MobEffects.REGENERATION, j.med.regenTicks, 0, false, false, true));
        p.level().playSound(null, p.blockPosition(), SoundEvents.PLAYER_BURP, SoundSource.PLAYERS, 0.4f, 1.4f);
        stop(p, j.restore);
    }

    private static void stop(ServerPlayer p, int restore) {
        JOBS.remove(p.getUUID());
        slow(p, 0);
        Net.to(p, new Net.HealSync(-1, 0, restore));
    }

    private static void slow(ServerPlayer p, double amount) {
        AttributeInstance a = p.getAttribute(Attributes.MOVEMENT_SPEED);
        if (a == null) return;
        a.removeModifier(SLOW);
        if (amount != 0) a.addTransientModifier(new AttributeModifier(SLOW, "ln_heal", amount, AttributeModifier.Operation.MULTIPLY_TOTAL));
    }
}
