package dev.longnight.lnai;

import java.util.ArrayList;
import java.util.List;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.TickEvent;

/**
 * 每 10 tick 把所有真人玩家的狀態（血量、護甲、醫療品、位置、P1～P4 編號）送給每位玩家，
 * 給左上小隊欄、羅盤和頭上標記用。編號依加入伺服器的順序。
 */
public final class TeamSync {
    private TeamSync() {}

    /** 測試用：把 NPC 隊友也當成真人玩家回報（/lnhud teamdebug on），單人也能看到多人版面 */
    static boolean debug = false;

    static void onTick(TickEvent.ServerTickEvent e) {
        if (e.phase != TickEvent.Phase.END) return;
        MinecraftServer s = net.minecraftforge.server.ServerLifecycleHooks.getCurrentServer();
        if (s == null || s.getTickCount() % 10 != 0) return;
        List<Net.Mate> mates = new ArrayList<>();
        int idx = 0;
        for (ServerPlayer p : s.getPlayerList().getPlayers()) {
            if (p.isSpectator()) continue;
            mates.add(mate(p, p.getGameProfile().getName(), idx++, p.getId(), meds(p)));
        }
        if (debug) {
            String[] fake = {"Kestrel_07", "OrangeTabby", "nightowl"};
            int k = 0;
            for (var lvl : s.getAllLevels())
                for (var en : lvl.getAllEntities())
                    if (en instanceof Mob m && m.getTags().contains("ln_ally") && !m.getTags().contains("ln_officer") && k < 3 && idx < 4)
                        mates.add(mate(m, fake[k++], idx++, m.getId(), k == 2 ? 0 : 3));
        }
        Net.Team msg = new Net.Team(mates);
        for (ServerPlayer p : s.getPlayerList().getPlayers()) Net.to(p, msg);
    }

    private static Net.Mate mate(LivingEntity e, String name, int idx, int id, int meds) {
        float armor = -1;
        for (EquipmentSlot sl : new EquipmentSlot[]{EquipmentSlot.HEAD, EquipmentSlot.CHEST}) {
            ItemStack st = e.getItemBySlot(sl);
            if (st.isEmpty()) continue;
            float d = !st.isDamageableItem() || st.getMaxDamage() <= 0 ? 1 : 1 - (float) st.getDamageValue() / st.getMaxDamage();
            armor = armor < 0 ? d / 2 : armor + d / 2;
        }
        return new Net.Mate(id, name, idx, e.getHealth(), e.getMaxHealth(), armor, meds,
                !e.isAlive() || e.isDeadOrDying(), e.getX(), e.getY(), e.getZ());
    }

    private static int meds(ServerPlayer p) {
        int n = 0;
        for (ItemStack st : p.getInventory().items)
            for (var reg : ModItems.MEDS.values()) if (st.is(reg.get())) n += st.getCount();
        return n;
    }
}
