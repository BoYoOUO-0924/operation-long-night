package dev.longnight.lnai.client;

import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.ArrayDeque;
import java.util.Deque;
import java.util.List;
import dev.longnight.lnai.Gear;
import dev.longnight.lnai.LnAi;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.world.InteractionHand;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

/**
 * 開發用：讓 Claude 不用操作滑鼠鍵盤也能測試介面。
 * 在遊戲資料夾放 lnai_debug.txt（每行一個指令），模組會依序執行後刪掉檔案：
 *   shot 名稱 | close | slot N | wheel g|m 選項 | use | release | look 水平 垂直 | wait 刻數 | tap 4|5 | nopause
 * 檔案不存在時完全不做事。
 */
@Mod.EventBusSubscriber(modid = LnAi.MODID, value = Dist.CLIENT)
public final class DebugHook {
    private DebugHook() {}

    private static final Logger LOG = LogUtils.getLogger();
    private static final Deque<String> QUEUE = new ArrayDeque<>();
    private static int wait = 0, poll = 0;

    @SubscribeEvent
    public static void tick(TickEvent.ClientTickEvent e) {
        if (e.phase != TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getInstance();
        if (QUEUE.isEmpty() && ++poll >= 20) {
            poll = 0;
            File f = new File(mc.gameDirectory, "lnai_debug.txt");
            if (f.isFile()) {
                try {
                    List<String> lines = Files.readAllLines(f.toPath(), StandardCharsets.UTF_8);
                    Files.delete(f.toPath());
                    for (String l : lines) if (!l.isBlank()) QUEUE.add(l.trim());
                } catch (Exception ex) { LOG.warn("[lnai-debug] {}", ex.toString()); }
            }
        }
        if (wait > 0) { wait--; return; }
        while (!QUEUE.isEmpty() && wait == 0) run(mc, QUEUE.poll());
    }

    static void run(Minecraft mc, String cmd) {
        String[] a = cmd.split(" ");
        LOG.info("[lnai-debug] {}", cmd);
        try {
            switch (a[0]) {
                case "shot" -> Screenshot.grab(mc.gameDirectory, a[1] + ".png", mc.getMainRenderTarget(), c -> LOG.info("[lnai-debug] saved {}", a[1]));
                case "close" -> mc.setScreen(null);
                case "nopause" -> { mc.options.pauseOnLostFocus = false; mc.setScreen(null); }
                case "slot" -> mc.player.getInventory().selected = Integer.parseInt(a[1]);
                case "wheel" -> {
                    WheelScreen w = new WheelScreen(a[1].equals("g"), -1, mc.player.getInventory().selected);
                    w.forced = a.length > 2 ? Integer.parseInt(a[2]) : -1;
                    mc.setScreen(w);
                }
                case "confirm" -> { if (mc.screen instanceof WheelScreen w) w.confirm(); }
                case "use" -> { KeyMapping.set(mc.options.keyUse.getKey(), true); mc.gameMode.useItem(mc.player, InteractionHand.MAIN_HAND); }
                case "release" -> KeyMapping.set(mc.options.keyUse.getKey(), false);
                case "look" -> { mc.player.setYRot(Float.parseFloat(a[1])); mc.player.setXRot(Float.parseFloat(a[2])); }
                case "wait" -> wait = Integer.parseInt(a[1]);
                case "key", "down", "up" -> {   // 模擬真的鍵盤事件：key = 按一下，down／up = 按住／放開
                    int code = com.mojang.blaze3d.platform.InputConstants.getKey("key.keyboard." + a[1]).getValue();
                    long win = mc.getWindow().getWindow();
                    if (!a[0].equals("up")) mc.keyboardHandler.keyPress(win, code, 0, org.lwjgl.glfw.GLFW.GLFW_PRESS, 0);
                    if (!a[0].equals("down")) mc.keyboardHandler.keyPress(win, code, 0, org.lwjgl.glfw.GLFW.GLFW_RELEASE, 0);
                }
                case "sidearm" -> {   // sidearm px py pz rx ry rz scale hand(0/1)
                    NpcSidearm.px = Float.parseFloat(a[1]); NpcSidearm.py = Float.parseFloat(a[2]); NpcSidearm.pz = Float.parseFloat(a[3]);
                    NpcSidearm.rx = Float.parseFloat(a[4]); NpcSidearm.ry = Float.parseFloat(a[5]); NpcSidearm.rz = Float.parseFloat(a[6]);
                    NpcSidearm.sc = Float.parseFloat(a[7]); NpcSidearm.hand = a[8].equals("1");
                }
                case "melee" -> dev.longnight.lnai.Net.CH.sendToServer(new dev.longnight.lnai.Net.Action(dev.longnight.lnai.Net.Action.MELEE, 0, mc.player.getInventory().selected));
                case "tap" -> {
                    int which = a[1].equals("4") ? Gear.SLOT_GRENADE : Gear.SLOT_MED;
                    ClientInput.prevSlot = mc.player.getInventory().selected;
                    mc.player.getInventory().selected = which;
                    ClientInput.tap(which);
                }
                default -> LOG.warn("[lnai-debug] unknown {}", cmd);
            }
        } catch (Exception ex) { LOG.warn("[lnai-debug] {} failed: {}", cmd, ex.toString()); }
    }
}
