package dev.longnight.lnai.client;

import com.mojang.blaze3d.platform.InputConstants;
import com.mojang.logging.LogUtils;
import dev.longnight.lnai.LnAi;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.settings.KeyModifier;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.slf4j.Logger;

/**
 * 統一按鍵：第一次開遊戲（載入完成時）把 assets/lnai/keys.txt 的按鍵套用到所有按鍵設定並存檔。
 * 套用過就在 config/lnai-keys.txt 記下版本，之後玩家自己改按鍵不會再被蓋掉；keys.txt 內容變了才會再套用一次。
 */
@Mod.EventBusSubscriber(modid = LnAi.MODID, value = Dist.CLIENT)
public final class KeyDefaults {
    private KeyDefaults() {}

    private static final Logger LOG = LogUtils.getLogger();
    private static boolean checked = false;

    /** 遊戲載入完（資源載入畫面結束）後的第一個 tick 執行一次；直接連伺服器、不經過主選單也會套用 */
    @SubscribeEvent
    public static void onTick(net.minecraftforge.event.TickEvent.ClientTickEvent e) {
        if (checked || e.phase != net.minecraftforge.event.TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getInstance();
        if (mc.options == null || mc.getOverlay() != null) return;
        checked = true;
        try { apply(Minecraft.getInstance()); }
        catch (Exception ex) { LOG.warn("[lnai] key defaults failed: {}", ex.toString()); }
    }

    private static void apply(Minecraft mc) throws Exception {
        String text;
        try (InputStream in = KeyDefaults.class.getResourceAsStream("/assets/lnai/keys.txt")) {
            if (in == null) return;
            text = new String(in.readAllBytes(), StandardCharsets.UTF_8);
        }
        String ver = Integer.toHexString(text.hashCode());
        Path marker = mc.gameDirectory.toPath().resolve("config/lnai-keys.txt");
        if (Files.exists(marker) && Files.readString(marker).trim().equals(ver)) return;

        Map<String, String> want = new HashMap<>();
        for (String line : text.split("\n")) {
            line = line.trim();
            if (!line.startsWith("key_")) continue;
            int c = line.indexOf(':');
            if (c > 0) want.put(line.substring(4, c), line.substring(c + 1));
        }
        int n = 0;
        for (KeyMapping km : mc.options.keyMappings) {
            String v = want.get(km.getName());
            if (v == null) continue;
            KeyModifier mod = KeyModifier.NONE;
            int c = v.lastIndexOf(':');
            if (c > 0) { mod = KeyModifier.valueFromString(v.substring(c + 1)); v = v.substring(0, c); }
            km.setKeyModifierAndCode(mod, InputConstants.getKey(v));
            n++;
        }
        KeyMapping.resetMapping();
        mc.options.save();
        Files.createDirectories(marker.getParent());
        Files.writeString(marker, ver);
        LOG.info("[lnai] applied {} key bindings from keys.txt ({})", n, ver);
    }
}
