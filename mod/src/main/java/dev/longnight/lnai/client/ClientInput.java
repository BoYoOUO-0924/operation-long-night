package dev.longnight.lnai.client;

import com.mojang.blaze3d.platform.InputConstants;
import dev.longnight.lnai.Gear;
import dev.longnight.lnai.LnAi;
import dev.longnight.lnai.Net;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.InputEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.lwjgl.glfw.GLFW;

/**
 * 按鍵：4 投擲物、5 醫療（沿用原版「快捷欄 4、5」的按鍵設定）。
 * 短按 → 4 拿出記住的投擲物；5 自動挑需要的醫療用品並開始使用。
 * 長按 → 開輪盤選擇，放開按鍵確認。
 * 另外：故事模式下快捷欄只到 5，滾輪在 1～5 之間循環。
 */
@Mod.EventBusSubscriber(modid = LnAi.MODID, value = Dist.CLIENT)
public final class ClientInput {
    private ClientInput() {}

    static final int HOLD_TICKS = 5;   // 按住 0.25 秒算長按
    static int heldKey = -1;          // 3 = 投擲、4 = 醫療
    static int heldTicks = 0;
    static int prevSlot = 0;
    static int lastValidSlot = 0;

    static boolean active(LocalPlayer p) {
        return p != null && !p.isCreative() && !p.isSpectator();
    }

    static int keyOf(int hotbar) {
        InputConstants.Key k = Minecraft.getInstance().options.keyHotbarSlots[hotbar].getKey();
        return k.getType() == InputConstants.Type.KEYSYM ? k.getValue() : -999;
    }

    @SubscribeEvent
    public static void onKey(InputEvent.Key e) {
        Minecraft mc = Minecraft.getInstance();
        if (!active(mc.player) || mc.screen != null) return;
        int which = e.getKey() == keyOf(Gear.SLOT_GRENADE) ? Gear.SLOT_GRENADE : e.getKey() == keyOf(Gear.SLOT_MED) ? Gear.SLOT_MED : -1;
        if (which < 0) return;
        if (e.getAction() == GLFW.GLFW_PRESS && heldKey < 0) {
            heldKey = which;
            heldTicks = 0;
            int sel = mc.player.getInventory().selected;
            prevSlot = sel == Gear.SLOT_MED ? lastValidSlot : sel;   // 原版會在這之後才切欄位
        } else if (e.getAction() == GLFW.GLFW_RELEASE && heldKey == which) {
            heldKey = -1;
            if (heldTicks < HOLD_TICKS) tap(which);
        }
    }

    static void tap(int which) {
        Minecraft mc = Minecraft.getInstance();
        if (which == Gear.SLOT_GRENADE) {
            Gear.Grenade g = pickGrenade(mc.player.getInventory(), ClientState.grenade);
            if (g != null) { ClientState.grenade = g; Net.CH.sendToServer(new Net.Action(Net.Action.GRENADE, g.ordinal(), prevSlot)); }
            mc.player.getInventory().selected = Gear.SLOT_GRENADE;
        } else {
            Net.CH.sendToServer(new Net.Action(Net.Action.MED_AUTO, 0, prevSlot));
        }
    }

    /** 記住的種類用完了，就換成還有的種類。 */
    static Gear.Grenade pickGrenade(Inventory inv, Gear.Grenade want) {
        if (count(inv, want) > 0) return want;
        for (Gear.Grenade g : Gear.Grenade.values()) if (count(inv, g) > 0) return g;
        return null;
    }

    static int count(Inventory inv, Gear.Grenade g) {
        int n = 0;
        for (var s : inv.items) if (g.is(s)) n += s.getCount();
        return n;
    }

    static int count(Inventory inv, Gear.Med m) {
        int n = 0;
        for (var s : inv.items) if (m.is(s)) n += s.getCount();
        return n;
    }

    @SubscribeEvent
    public static void onTick(TickEvent.ClientTickEvent e) {
        if (e.phase != TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getInstance();
        if (!active(mc.player)) { heldKey = -1; return; }
        Inventory inv = mc.player.getInventory();
        if (inv.selected > Gear.LAST_SLOT) inv.selected = lastValidSlot;   // 6～9 鎖住
        if (inv.selected != Gear.SLOT_MED) lastValidSlot = inv.selected;
        if (heldKey >= 0 && mc.screen == null) {
            if (++heldTicks == HOLD_TICKS) mc.setScreen(new WheelScreen(heldKey == Gear.SLOT_GRENADE, keyOf(heldKey), prevSlot));
        }
    }

    @SubscribeEvent
    public static void onScroll(InputEvent.MouseScrollingEvent e) {
        Minecraft mc = Minecraft.getInstance();
        if (!active(mc.player) || mc.screen != null) return;
        e.setCanceled(true);
        Inventory inv = mc.player.getInventory();
        int dir = e.getScrollDelta() > 0 ? -1 : 1;
        int n = Gear.LAST_SLOT + 1;
        inv.selected = ((inv.selected + dir) % n + n) % n;
    }
}
