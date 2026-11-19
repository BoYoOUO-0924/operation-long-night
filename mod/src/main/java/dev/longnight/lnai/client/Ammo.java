package dev.longnight.lnai.client;

import java.lang.reflect.Method;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.ForgeRegistries;

/** 讀 TaCZ 槍的彈匣數、備彈、射擊模式（用反射，不直接依賴 TaCZ）。 */
final class Ammo {
    private Ammo() {}

    record Info(String name, int mag, int reserve, String mode) {}

    private static final ResourceLocation GUN = new ResourceLocation("tacz", "modern_kinetic_gun");
    private static final ResourceLocation AMMO = new ResourceLocation("tacz", "ammo");
    private static final Map<String, String> AMMO_OF = new HashMap<>();
    private static Method getIndex, getGunData, getAmmoId;

    static boolean isGun(ItemStack s) { return !s.isEmpty() && GUN.equals(ForgeRegistries.ITEMS.getKey(s.getItem())); }

    static Info of(ItemStack s, Inventory inv) {
        if (!isGun(s)) return null;
        CompoundTag t = s.getOrCreateTag();
        String gunId = t.getString("GunId");
        int mag = t.getInt("GunCurrentAmmoCount") + (t.getBoolean("HasBulletInBarrel") ? 1 : 0);
        String mode = switch (t.getString("GunFireMode")) {
            case "AUTO" -> "全自動";
            case "BURST" -> "連發";
            case "SEMI" -> "半自動";
            default -> "";
        };
        String ammoId = ammoOf(gunId);
        int reserve = -1;
        if (ammoId != null) {
            reserve = 0;
            for (ItemStack i : inv.items)
                if (!i.isEmpty() && AMMO.equals(ForgeRegistries.ITEMS.getKey(i.getItem())) && i.hasTag() && ammoId.equals(i.getTag().getString("AmmoId")))
                    reserve += i.getCount();
        }
        return new Info(s.getHoverName().getString(), mag, reserve, mode);
    }

    private static String ammoOf(String gunId) {
        if (gunId.isEmpty()) return null;
        return AMMO_OF.computeIfAbsent(gunId, id -> {
            try {
                if (getIndex == null) {
                    Class<?> api = Class.forName("com.tacz.guns.api.TimelessAPI");
                    getIndex = api.getMethod("getClientGunIndex", ResourceLocation.class);
                    getGunData = Class.forName("com.tacz.guns.client.resource.index.ClientGunIndex").getMethod("getGunData");
                    getAmmoId = Class.forName("com.tacz.guns.resource.pojo.data.gun.GunData").getMethod("getAmmoId");
                }
                Optional<?> idx = (Optional<?>) getIndex.invoke(null, new ResourceLocation(id));
                if (idx.isEmpty()) return null;
                Object data = getGunData.invoke(idx.get());
                return getAmmoId.invoke(data).toString();
            } catch (Throwable e) {
                return null;
            }
        });
    }
}
