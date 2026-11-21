package dev.longnight.lnai;

import com.mojang.logging.LogUtils;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.registries.ForgeRegistries;
import org.slf4j.Logger;

/**
 * 改槍台（伺服器端）：手持槍右鍵 TaCZ 改槍工作台 → 打開改槍介面（Z 鍵改槍已停用）。
 *
 * TaCZ 的改槍介面只列出「背包裡」有的配件，所以改槍期間先把背包（第 10～36 格）收起來，
 * 依玩家在介面上點的配件種類（瞄具、槍口……），把這把槍能裝的該類配件全部放進背包讓他選；
 * 關掉介面或離開工作台就把背包還原。裝上槍的配件留在槍上。
 */
final class Refit {
    private Refit() {}

    private static final Logger LOG = LogUtils.getLogger();
    private static final ResourceLocation TABLE = new ResourceLocation("tacz", "gun_smith_table");
    private static final int FIRST = 9, LAST = 35;      // 背包（不含快捷欄）

    private record Session(List<ItemStack> backup, BlockPos at, int gunSlot) {}

    private static final Map<UUID, Session> SESSIONS = new HashMap<>();

    // ---------------------------------------------------------------- 事件
    static void onRightClickBlock(PlayerInteractEvent.RightClickBlock e) {
        if (!(e.getEntity() instanceof ServerPlayer p)) return;
        if (!TABLE.equals(ForgeRegistries.BLOCKS.getKey(e.getLevel().getBlockState(e.getPos()).getBlock()))) return;
        e.setCanceled(true);                              // 不開 TaCZ 的製作介面
        e.setCancellationResult(InteractionResult.SUCCESS);
        if (e.getHand() != InteractionHand.MAIN_HAND) return;
        if (!isGun(p.getMainHandItem())) {
            p.displayClientMessage(Component.literal("手持要改的槍，再點改槍台"), true);
            return;
        }
        start(p, e.getPos());
    }

    static void onTick(TickEvent.PlayerTickEvent e) {
        if (e.phase != TickEvent.Phase.END || !(e.player instanceof ServerPlayer p)) return;
        Session s = SESSIONS.get(p.getUUID());
        if (s == null) return;
        // 離開工作台、換手上的格子、倒地或死亡 → 結束
        if (!p.isAlive() || p.distanceToSqr(s.at.getX() + 0.5, s.at.getY() + 0.5, s.at.getZ() + 0.5) > 36
                || p.getInventory().selected != s.gunSlot || Downed.isDowned(p)) end(p);
    }

    static void onLogout(PlayerEvent.PlayerLoggedOutEvent e) {
        if (e.getEntity() instanceof ServerPlayer p) end(p);
    }

    /** 玩家端回報：介面上選了哪一類配件（NONE = 總覽），或關掉了介面（type = null） */
    static void onClient(ServerPlayer p, String type) {
        if ("START".equals(type)) {                       // 玩家拿槍對著改槍台按右鍵（確認真的對著工作台）
            if (p.pick(5.0, 1f, false) instanceof net.minecraft.world.phys.BlockHitResult bh
                    && TABLE.equals(ForgeRegistries.BLOCKS.getKey(p.level().getBlockState(bh.getBlockPos()).getBlock()))) {
                if (isGun(p.getMainHandItem())) start(p, bh.getBlockPos());
                else p.displayClientMessage(Component.literal("手持要改的槍，再點改槍台"), true);
            }
            return;
        }
        if (!SESSIONS.containsKey(p.getUUID())) return;
        if (type == null) { end(p); return; }
        fill(p, type);
    }

    // ---------------------------------------------------------------- 流程
    private static void start(ServerPlayer p, BlockPos at) {
        if (SESSIONS.containsKey(p.getUUID())) return;
        Inventory inv = p.getInventory();
        List<ItemStack> backup = new ArrayList<>();
        for (int i = FIRST; i <= LAST; i++) {
            backup.add(inv.getItem(i).copy());
            inv.setItem(i, ItemStack.EMPTY);
        }
        SESSIONS.put(p.getUUID(), new Session(backup, at.immutable(), inv.selected));
        inv.setChanged();
        p.containerMenu.broadcastChanges();
        Net.to(p, new Net.RefitOpen());
        p.level().playSound(null, at, net.minecraft.sounds.SoundEvents.ARMOR_EQUIP_IRON, net.minecraft.sounds.SoundSource.PLAYERS, 0.8f, 1.2f);
    }

    static void end(ServerPlayer p) {
        Session s = SESSIONS.remove(p.getUUID());
        if (s == null) return;
        Inventory inv = p.getInventory();
        for (int i = FIRST; i <= LAST; i++) inv.setItem(i, s.backup.get(i - FIRST));
        inv.setChanged();
        p.containerMenu.broadcastChanges();
    }

    private static void fill(ServerPlayer p, String typeName) {
        Inventory inv = p.getInventory();
        for (int i = FIRST; i <= LAST; i++) inv.setItem(i, ItemStack.EMPTY);
        ItemStack gun = p.getMainHandItem();
        if (!"NONE".equals(typeName) && isGun(gun)) {
            int slot = FIRST;
            for (ItemStack a : compatible(gun, typeName)) {
                if (slot > LAST) break;
                inv.setItem(slot++, a);
            }
        }
        inv.setChanged();
        p.containerMenu.broadcastChanges();
    }

    // ---------------------------------------------------------------- TaCZ（反射）
    private static Method getIGun, allow, allIndex, idxType, idxSort;

    private static void init() throws Exception {
        if (getIGun != null) return;
        Class<?> ig = Class.forName("com.tacz.guns.api.item.IGun");
        getIGun = ig.getMethod("getIGunOrNull", ItemStack.class);
        allow = ig.getMethod("allowAttachment", ItemStack.class, ItemStack.class);
        allIndex = Class.forName("com.tacz.guns.api.TimelessAPI").getMethod("getAllCommonAttachmentIndex");
        Class<?> ci = Class.forName("com.tacz.guns.resource.index.CommonAttachmentIndex");
        idxType = ci.getMethod("getType");
        idxSort = ci.getMethod("getSort");
    }

    static boolean isGun(ItemStack s) {
        try { init(); return !s.isEmpty() && getIGun.invoke(null, s) != null; }
        catch (Throwable t) { return false; }
    }

    /** 這把槍能裝的某一類配件（依 TaCZ 的排序） */
    private static List<ItemStack> compatible(ItemStack gun, String typeName) {
        List<ItemStack> out = new ArrayList<>();
        try {
            init();
            Object ig = getIGun.invoke(null, gun);
            Item att = ForgeRegistries.ITEMS.getValue(new ResourceLocation("tacz", "attachment"));
            List<Object[]> found = new ArrayList<>();
            for (Object o : (java.util.Set<?>) allIndex.invoke(null)) {
                Map.Entry<?, ?> en = (Map.Entry<?, ?>) o;
                Object idx = en.getValue();
                if (!typeName.equals(String.valueOf(idxType.invoke(idx)))) continue;
                ItemStack a = new ItemStack(att);
                a.getOrCreateTag().putString("AttachmentId", en.getKey().toString());
                if ((boolean) allow.invoke(ig, gun, a)) found.add(new Object[]{idxSort.invoke(idx), en.getKey().toString(), a});
            }
            found.sort((x, y) -> {
                int c = Integer.compare((int) x[0], (int) y[0]);
                return c != 0 ? c : ((String) x[1]).compareTo((String) y[1]);
            });
            for (Object[] f : found) out.add((ItemStack) f[2]);
        } catch (Throwable t) {
            LOG.warn("[lnai] refit: listing attachments failed: {}", t.toString());
        }
        return out;
    }
}
