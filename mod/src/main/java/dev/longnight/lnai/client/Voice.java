package dev.longnight.lnai.client;

import dev.longnight.lnai.LnAi;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.HashMap;
import java.util.Map;
import net.minecraft.client.Minecraft;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.client.resources.sounds.SoundInstance;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;

/**
 * 角色語音：字幕出現時找對應的語音檔（tools/make_voices.py 產生）來播。
 * <ul>
 *   <li>編號 = sha1(說話的人 + "|" + 去掉標點的台詞) 前 12 碼，和產生腳本相同</li>
 *   <li>過場：直接播原聲</li>
 *   <li>遊玩中：說話的 NPC 在 20 格內 → 從他的位置播原聲；比較遠或看不到 → 無線電版（對講機音質）</li>
 *   <li>同一個人講新的一句時，切掉他上一句</li>
 * </ul>
 */
public final class Voice {
    private Voice() {}

    static final double NEAR = 20;
    private static final Map<String, SoundInstance> LAST = new HashMap<>();

    static String id(String who, String text) {
        StringBuilder c = new StringBuilder();
        text.codePoints().filter(Character::isLetterOrDigit).forEach(c::appendCodePoint);
        try {
            byte[] h = MessageDigest.getInstance("SHA-1").digest((who + "|" + c).getBytes(StandardCharsets.UTF_8));
            StringBuilder s = new StringBuilder();
            for (int i = 0; i < 6; i++) s.append(String.format("%02x", h[i]));
            return s.toString();
        } catch (Exception e) {
            return "";
        }
    }

    public static void play(String who, String text, boolean cutscene) {
        if (who == null || who.isEmpty()) return;
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null || mc.player == null) return;
        String id = id(who, text);
        Entity speaker = cutscene ? null : find(who);
        boolean radioLine = text.contains("（無線電）") || text.contains("(無線電)");   // 劇本標明是無線電
        boolean near = !radioLine && (cutscene || (speaker != null && speaker.distanceTo(mc.player) <= NEAR));
        ResourceLocation rl = new ResourceLocation(LnAi.MODID, "voice." + id + (near ? "" : ".radio"));
        if (mc.getSoundManager().getSoundEvent(rl) == null) {   // 這句還沒有語音
            com.mojang.logging.LogUtils.getLogger().debug("[lnai] no voice for {} {}", who, id);
            return;
        }
        com.mojang.logging.LogUtils.getLogger().info("[lnai] voice {} {} ({})", who, id, near ? (speaker != null ? "near" : "cutscene") : "radio");
        SoundInstance old = LAST.remove(who);
        if (old != null) mc.getSoundManager().stop(old);
        SoundInstance s;
        if (near && speaker != null)
            s = new SimpleSoundInstance(rl, SoundSource.VOICE, 1.3f, 1f, SoundInstance.createUnseededRandom(), false, 0,
                    SoundInstance.Attenuation.LINEAR, speaker.getX(), speaker.getEyeY(), speaker.getZ(), false);
        else
            s = new SimpleSoundInstance(rl, SoundSource.VOICE, near ? 1f : 0.85f, 1f, SoundInstance.createUnseededRandom(), false, 0,
                    SoundInstance.Attenuation.NONE, 0, 0, 0, true);
        mc.getSoundManager().play(s);
        LAST.put(who, s);
    }

    /** 找名字是 who 的 NPC（最近的那個） */
    private static Entity find(String who) {
        Minecraft mc = Minecraft.getInstance();
        Entity best = null;
        double bd = Double.MAX_VALUE;
        for (Entity e : mc.level.entitiesForRendering()) {
            if (e instanceof Player || !e.hasCustomName() || !who.equals(e.getCustomName().getString())) continue;
            double d = e.distanceToSqr(mc.player);
            if (d < bd) { bd = d; best = e; }
        }
        return best;
    }
}
