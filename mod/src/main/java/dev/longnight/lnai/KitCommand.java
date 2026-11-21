package dev.longnight.lnai;

import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.logging.LogUtils;
import java.lang.reflect.Method;
import java.util.Collection;
import java.util.Optional;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.registries.ForgeRegistries;
import org.slf4j.Logger;

/**
 * 大廳軍械庫與各章裝備（自由配槍）：
 * /lnkit gun <玩家> <槍ID> [配件ID,配件ID...]   發一把滿彈匣的槍：手槍放第 2 格，其他放第 1 格
 * /lnkit ammo <玩家> <主武器彈匣數> <副武器彈匣數> fill|add
 *       依手上兩把槍的口徑發子彈；fill = 補到這個數量為止，add = 直接加
 * /lnkit stash <玩家>       跳傘前記下身上的兩把槍（含配件），進關卡後 restore 會還回來
 * /lnkit restore <玩家> <預設主武器> <預設副武器>   還原記下的槍；沒記過就發該章預設武器（none = 不發）
 * /lnkit forget <玩家>      清掉記下的槍
 */
final class KitCommand {
    private KitCommand() {}

    private static final Logger LOG = LogUtils.getLogger();
    private static final String KEY = "ln_guns";

    static void register(RegisterCommandsEvent e) {
        e.getDispatcher().register(Commands.literal("lnkit").requires(s -> s.hasPermission(2))
                .then(Commands.literal("gun").then(Commands.argument("p", EntityArgument.players())
                        .then(Commands.argument("id", StringArgumentType.string()).executes(c -> gun(c, ""))
                                .then(Commands.argument("att", StringArgumentType.greedyString())
                                        .executes(c -> gun(c, StringArgumentType.getString(c, "att")))))))
                .then(Commands.literal("ammo").then(Commands.argument("p", EntityArgument.players())
                        .then(Commands.argument("pri", IntegerArgumentType.integer(0, 20))
                                .then(Commands.argument("sec", IntegerArgumentType.integer(0, 20))
                                        .then(Commands.literal("fill").executes(c -> ammo(c, true)))
                                        .then(Commands.literal("add").executes(c -> ammo(c, false)))))))
                .then(Commands.literal("stash").then(Commands.argument("p", EntityArgument.players()).executes(KitCommand::stash)))
                .then(Commands.literal("forget").then(Commands.argument("p", EntityArgument.players()).executes(c -> {
                    for (ServerPlayer p : EntityArgument.getPlayers(c, "p")) persisted(p).remove(KEY);
                    return 1;
                })))
                .then(Commands.literal("restore").then(Commands.argument("p", EntityArgument.players())
                        .then(Commands.argument("pri", StringArgumentType.string())
                                .then(Commands.argument("sec", StringArgumentType.string()).executes(KitCommand::restore))))));
    }

    // ---------------------------------------------------------------- 指令
    private static int gun(CommandContext<CommandSourceStack> c, String att) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        String id = StringArgumentType.getString(c, "id");
        Collection<ServerPlayer> ps = EntityArgument.getPlayers(c, "p");
        for (ServerPlayer p : ps) {
            ItemStack g = makeGun(id, att);
            if (g.isEmpty()) { c.getSource().sendFailure(net.minecraft.network.chat.Component.literal("沒有這把槍：" + id)); return 0; }
            p.getInventory().setItem(isPistol(id) ? 1 : 0, g);
            p.getInventory().setChanged();
        }
        return ps.size();
    }

    private static int ammo(CommandContext<CommandSourceStack> c, boolean fill) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        int pri = IntegerArgumentType.getInteger(c, "pri"), sec = IntegerArgumentType.getInteger(c, "sec");
        Collection<ServerPlayer> ps = EntityArgument.getPlayers(c, "p");
        for (ServerPlayer p : ps) {
            Inventory inv = p.getInventory();
            String a0 = gunId(inv.getItem(0)), a1 = gunId(inv.getItem(1));
            // 兩把槍口徑一樣（例如都打 9mm）就合併計算
            java.util.Map<String, Integer> want = new java.util.LinkedHashMap<>();
            if (a0 != null) want.merge(ammoOf(a0), capacity(a0) * pri, Integer::sum);
            if (a1 != null) want.merge(ammoOf(a1), capacity(a1) * sec, Integer::sum);
            for (var en : want.entrySet()) {
                if (en.getKey() == null) continue;
                int n = en.getValue() - (fill ? countAmmo(inv, en.getKey()) : 0);
                giveAmmo(p, en.getKey(), n);
            }
        }
        return ps.size();
    }

    private static int stash(CommandContext<CommandSourceStack> c) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        Collection<ServerPlayer> ps = EntityArgument.getPlayers(c, "p");
        for (ServerPlayer p : ps) {
            CompoundTag t = new CompoundTag();
            for (int i = 0; i < 2; i++) {
                ItemStack s = p.getInventory().getItem(i);
                if (gunId(s) != null) t.put("s" + i, s.save(new CompoundTag()));
            }
            if (t.isEmpty()) persisted(p).remove(KEY);
            else persisted(p).put(KEY, t);
        }
        return ps.size();
    }

    private static int restore(CommandContext<CommandSourceStack> c) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        String[] def = {StringArgumentType.getString(c, "pri"), StringArgumentType.getString(c, "sec")};
        Collection<ServerPlayer> ps = EntityArgument.getPlayers(c, "p");
        for (ServerPlayer p : ps) {
            CompoundTag t = persisted(p).getCompound(KEY);
            for (int i = 0; i < 2; i++) {
                ItemStack s = t.contains("s" + i) ? ItemStack.of(t.getCompound("s" + i)) : ItemStack.EMPTY;
                if (s.isEmpty() && !def[i].equals("none")) s = makeGun(def[i], "");
                if (s.isEmpty()) continue;
                fillMag(s);
                p.getInventory().setItem(i, s);
            }
            p.getInventory().setChanged();
        }
        return ps.size();
    }

    // ---------------------------------------------------------------- 物品
    private static CompoundTag persisted(ServerPlayer p) {
        CompoundTag root = p.getPersistentData();
        if (!root.contains(Player.PERSISTED_NBT_TAG)) root.put(Player.PERSISTED_NBT_TAG, new CompoundTag());
        return root.getCompound(Player.PERSISTED_NBT_TAG);
    }

    static ItemStack makeGun(String id, String att) {
        if (!id.contains(":")) id = "tacz:" + id;
        if (index(id).isEmpty()) return ItemStack.EMPTY;
        Item gun = ForgeRegistries.ITEMS.getValue(new ResourceLocation("tacz", "modern_kinetic_gun"));
        Item attItem = ForgeRegistries.ITEMS.getValue(new ResourceLocation("tacz", "attachment"));
        ItemStack s = new ItemStack(gun);
        CompoundTag t = s.getOrCreateTag();
        t.putString("GunId", id);
        t.putString("GunFireMode", "UNKNOWN");
        t.putBoolean("HasBulletInBarrel", true);
        for (String a : att.split("[,\\s]+")) {
            if (a.isBlank()) continue;
            String[] kv = a.split("=", 2);          // 型別=配件ID，例如 SCOPE=tacz:sight_t2
            if (kv.length != 2) continue;
            ItemStack as = new ItemStack(attItem);
            as.getOrCreateTag().putString("AttachmentId", kv[1].contains(":") ? kv[1] : "tacz:" + kv[1]);
            t.put("Attachment" + kv[0].toUpperCase(), as.save(new CompoundTag()));
        }
        fillMag(s);
        return s;
    }

    private static void fillMag(ItemStack s) {
        String id = gunId(s);
        if (id == null) return;
        s.getOrCreateTag().putInt("GunCurrentAmmoCount", capacity(id));
        s.getOrCreateTag().putBoolean("HasBulletInBarrel", true);
    }

    private static String gunId(ItemStack s) {
        CompoundTag t = s.getTag();
        return t != null && t.contains("GunId") ? t.getString("GunId") : null;
    }

    private static int countAmmo(Inventory inv, String ammo) {
        int n = 0;
        for (ItemStack s : inv.items) {
            CompoundTag t = s.getTag();
            if (t != null && ammo.equals(t.getString("AmmoId")) && !t.contains("GunId")) n += s.getCount();
        }
        return n;
    }

    private static void giveAmmo(ServerPlayer p, String ammo, int n) {
        Item item = ForgeRegistries.ITEMS.getValue(new ResourceLocation("tacz", "ammo"));
        while (n > 0) {
            ItemStack s = new ItemStack(item);
            s.getOrCreateTag().putString("AmmoId", ammo);
            int k = Math.min(n, s.getMaxStackSize());
            s.setCount(k);
            n -= k;
            if (!p.getInventory().add(s)) p.drop(s, false);
        }
    }

    // ---------------------------------------------------------------- TaCZ 槍枝資料（反射，不直接依賴 TaCZ）
    private static Method getIndex, getGunData, getAmmoAmount, getAmmoId, getType;

    private static Optional<?> index(String id) {
        try {
            if (getIndex == null) {
                getIndex = Class.forName("com.tacz.guns.api.TimelessAPI").getMethod("getCommonGunIndex", ResourceLocation.class);
                Class<?> ci = Class.forName("com.tacz.guns.resource.index.CommonGunIndex");
                getGunData = ci.getMethod("getGunData");
                getType = ci.getMethod("getType");
                Class<?> gd = Class.forName("com.tacz.guns.resource.pojo.data.gun.GunData");
                getAmmoAmount = gd.getMethod("getAmmoAmount");
                getAmmoId = gd.getMethod("getAmmoId");
            }
            return (Optional<?>) getIndex.invoke(null, new ResourceLocation(id));
        } catch (Throwable t) {
            LOG.warn("[lnai] lnkit: TaCZ lookup failed for {}: {}", id, t.toString());
            return Optional.empty();
        }
    }

    static int capacity(String id) {
        try { Optional<?> i = index(id); return i.isEmpty() ? 30 : (int) getAmmoAmount.invoke(getGunData.invoke(i.get())); }
        catch (Throwable t) { return 30; }
    }

    static String ammoOf(String id) {
        try { Optional<?> i = index(id); return i.isEmpty() ? null : getAmmoId.invoke(getGunData.invoke(i.get())).toString(); }
        catch (Throwable t) { return null; }
    }

    static boolean isPistol(String id) {
        if (!id.contains(":")) id = "tacz:" + id;
        try { Optional<?> i = index(id); return i.isPresent() && "pistol".equals(String.valueOf(getType.invoke(i.get()))); }
        catch (Throwable t) { return false; }
    }
}
