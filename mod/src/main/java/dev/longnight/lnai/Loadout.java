package dev.longnight.lnai;

import java.util.function.Predicate;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.ItemStack;

/** 伺服器端：把指定的醫療用品／投擲物換到固定欄位上。 */
final class Loadout {
    private Loadout() {}

    static void handle(ServerPlayer p, Net.Action a) {
        if (p.isSpectator() || !p.isAlive()) return;
        switch (a.kind()) {
            case Net.Action.MED_AUTO -> {
                Gear.Med m = autoMed(p);
                if (m == null) { tell(p, p.getHealth() >= p.getMaxHealth() ? "生命值已滿" : "沒有醫療用品"); Net.to(p, new Net.HealSync(-1, 0, a.prevSlot())); return; }
                Heal.start(p, m, a.prevSlot());
            }
            case Net.Action.MED_PICK -> {
                if (a.arg() < 0 || a.arg() >= Gear.Med.values().length) return;
                Gear.Med m = Gear.Med.values()[a.arg()];
                if (count(p.getInventory(), m::is) == 0) { tell(p, "沒有" + m.label); Net.to(p, new Net.HealSync(-1, 0, a.prevSlot())); return; }
                Heal.start(p, m, a.prevSlot());
            }
            case Net.Action.GRENADE -> {
                if (a.arg() < 0 || a.arg() >= Gear.Grenade.values().length) return;
                Gear.Grenade g = Gear.Grenade.values()[a.arg()];
                if (!equip(p.getInventory(), Gear.SLOT_GRENADE, g::is)) tell(p, "沒有" + g.label);
            }
            default -> {}
        }
    }

    /** 短按 5：傷得重先用急救包，傷得輕用繃帶，最後才用止痛藥。 */
    static Gear.Med autoMed(ServerPlayer p) {
        float missing = p.getMaxHealth() - p.getHealth();
        if (missing < 0.5f) return null;
        Inventory inv = p.getInventory();
        boolean kit = count(inv, Gear.Med.MEDKIT::is) > 0, band = count(inv, Gear.Med.BANDAGE::is) > 0, pill = count(inv, Gear.Med.PAINKILLER::is) > 0;
        if (missing >= 8 && kit) return Gear.Med.MEDKIT;
        if (band) return Gear.Med.BANDAGE;
        if (kit) return Gear.Med.MEDKIT;
        if (pill) return Gear.Med.PAINKILLER;
        return null;
    }

    static int count(Inventory inv, Predicate<ItemStack> f) {
        int n = 0;
        for (int i = 0; i < inv.items.size(); i++) if (f.test(inv.items.get(i))) n += inv.items.get(i).getCount();
        return n;
    }

    /** 把符合條件的物品換到 slot；已經在那裡就不動。 */
    static boolean equip(Inventory inv, int slot, Predicate<ItemStack> f) {
        if (f.test(inv.getItem(slot))) return true;
        for (int i = 0; i < inv.items.size(); i++) {
            if (i == slot || !f.test(inv.items.get(i))) continue;
            ItemStack here = inv.getItem(slot);
            inv.setItem(slot, inv.items.get(i));
            inv.setItem(i, here);
            return true;
        }
        return false;
    }

    static void tell(ServerPlayer p, String msg) {
        p.displayClientMessage(Component.literal(msg).withStyle(s -> s.withColor(ChatFormatting.GRAY).withFont(LnAi.FONT)), true);
    }
}
