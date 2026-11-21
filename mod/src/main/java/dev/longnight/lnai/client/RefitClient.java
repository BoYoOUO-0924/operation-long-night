package dev.longnight.lnai.client;

import dev.longnight.lnai.LnAi;
import dev.longnight.lnai.Net;
import java.lang.reflect.Method;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ScreenEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * 改槍台（玩家端）：
 *  - Z 鍵不能再直接打開 TaCZ 改槍介面，只有伺服器（點改槍台）通知時才打開
 *  - 介面打開時回報目前選的配件種類，伺服器就把那一類能裝的配件放進背包
 *  - 背包內容變了就重建介面，讓新配件出現在清單上；關掉介面時通知伺服器還原背包
 */
@Mod.EventBusSubscriber(modid = LnAi.MODID, value = Dist.CLIENT)
public final class RefitClient {
    private RefitClient() {}

    private static final String SCREEN = "com.tacz.guns.client.gui.GunRefitScreen";
    private static boolean session = false, opening = false;
    private static String lastType = null;
    private static int lastSig = 0;
    private static Method currentType;

    /** 伺服器：玩家點了改槍台 */
    public static void open() {
        Minecraft mc = Minecraft.getInstance();
        try {
            Screen s = (Screen) Class.forName(SCREEN).getConstructor().newInstance();
            session = true;
            lastType = null;
            opening = true;
            mc.setScreen(s);
        } catch (Throwable t) {
            com.mojang.logging.LogUtils.getLogger().warn("[lnai] cannot open refit screen: {}", t.toString());
            Net.CH.sendToServer(new Net.RefitMsg(""));
        } finally {
            opening = false;
        }
    }

    private static boolean isRefit(Object s) { return s != null && s.getClass().getName().equals(SCREEN); }

    @SubscribeEvent
    public static void onOpen(ScreenEvent.Opening e) {
        if (isRefit(e.getNewScreen()) && !opening && !session) e.setCanceled(true);   // Z 鍵：不准開
    }

    private static boolean useWasDown = false;

    /** 右鍵（拿槍時 TaCZ 拿來瞄準，點方塊的動作不會送到伺服器）：對著改槍台按下就請伺服器開始改槍 */
    private static void checkUse(Minecraft mc) {
        boolean down = mc.options.keyUse.isDown();
        boolean pressed = down && !useWasDown;
        useWasDown = down;
        if (!pressed || session || mc.screen != null || mc.player == null) return;
        if (!(mc.hitResult instanceof net.minecraft.world.phys.BlockHitResult bh) || bh.getType() != net.minecraft.world.phys.HitResult.Type.BLOCK) return;
        var id = net.minecraftforge.registries.ForgeRegistries.BLOCKS.getKey(mc.level.getBlockState(bh.getBlockPos()).getBlock());
        if (id != null && id.toString().equals("tacz:gun_smith_table")) Net.CH.sendToServer(new Net.RefitMsg("START"));
    }

    @SubscribeEvent
    public static void tick(TickEvent.ClientTickEvent e) {
        if (e.phase != TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getInstance();
        checkUse(mc);
        if (!session) return;
        if (mc.player == null || !isRefit(mc.screen)) {      // 關掉了
            session = false;
            Net.CH.sendToServer(new Net.RefitMsg(""));
            return;
        }
        String type = "NONE";
        try {
            if (currentType == null)
                currentType = Class.forName("com.tacz.guns.client.animation.screen.RefitTransform").getMethod("getCurrentTransformType");
            type = String.valueOf(currentType.invoke(null));
        } catch (Throwable ignored) {}
        if (!type.equals(lastType)) {
            lastType = type;
            Net.CH.sendToServer(new Net.RefitMsg(type));
        }
        int sig = 1;
        for (int i = 9; i <= 35; i++) {
            ItemStack s = mc.player.getInventory().getItem(i);
            sig = sig * 31 + (s.isEmpty() ? 0 : s.getItem().hashCode() * 17 + java.util.Objects.hashCode(s.getTag()));
        }
        if (sig != lastSig) {                                   // 伺服器放了新配件 → 重建介面清單
            lastSig = sig;
            Screen s = mc.screen;
            s.init(mc, mc.getWindow().getGuiScaledWidth(), mc.getWindow().getGuiScaledHeight());
        }
    }
}
