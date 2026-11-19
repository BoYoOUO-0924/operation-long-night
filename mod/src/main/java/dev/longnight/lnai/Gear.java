package dev.longnight.lnai;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.ForgeRegistries;

/** 醫療用品與投擲物的種類定義（伺服器與玩家端共用）。 */
public final class Gear {
    private Gear() {}

    /** 快捷欄固定位置：1 主武器、2 副武器、3 近戰、4 投擲、5 醫療。 */
    public static final int SLOT_GRENADE = 3, SLOT_MED = 4, LAST_SLOT = 4;

    public enum Med {
        BANDAGE("bandage", "繃帶", "包紮中", 30, 3f, 0),
        PAINKILLER("painkiller", "止痛藥", "服藥中", 20, 1f, 300),
        MEDKIT("medkit", "急救包", "治療中", 80, 12f, 0);

        public final String id, label, verb;
        public final int ticks, regenTicks;
        public final float heal;

        Med(String id, String label, String verb, int ticks, float heal, int regenTicks) {
            this.id = id; this.label = label; this.verb = verb; this.ticks = ticks; this.heal = heal; this.regenTicks = regenTicks;
        }

        public Item item() { return ModItems.MEDS.get(this).get(); }

        public boolean is(ItemStack s) { return !s.isEmpty() && s.getItem() == item(); }

        public static Med of(ItemStack s) {
            for (Med m : values()) if (m.is(s)) return m;
            return null;
        }
    }

    public enum Grenade {
        // 物理數值以 /lnhud trace 實測（Superb Warfare 0.8.9.2）
        M67("superbwarfare:hand_grenade", "M67 破片", 10f, 1.5f, 0.05, 0.98, false),
        RGO("superbwarfare:rgo_grenade", "RGO 撞擊", 8f, 1.8f, 0.05, 1.0, true),
        SMOKE("superbwarfare:m18_smoke_grenade", "M18 煙霧", 10f, 1.5f, 0.07, 0.98, false);

        public final ResourceLocation id;
        public final String label;
        /** 投擲力道 = min(蓄力 tick / div, max)，與 Superb Warfare 的物品邏輯相同。 */
        public final float div, max;
        /** 每 tick：moveFirst ? (位置 += 速度; 速度.y -= g) : (速度 = (速度 - g) * drag; 位置 += 速度)。 */
        public final double gravity, drag;
        public final boolean moveFirst;

        Grenade(String id, String label, float div, float max, double gravity, double drag, boolean moveFirst) {
            this.id = new ResourceLocation(id); this.label = label; this.div = div; this.max = max;
            this.gravity = gravity; this.drag = drag; this.moveFirst = moveFirst;
        }

        public Item item() { return ForgeRegistries.ITEMS.getValue(id); }

        public boolean is(ItemStack s) { return !s.isEmpty() && s.getItem() == item(); }

        public float power(int useTicks) { return Math.min(useTicks / div, max); }

        public static Grenade of(ItemStack s) {
            for (Grenade g : values()) if (g.is(s)) return g;
            return null;
        }
    }
}
