package dev.longnight.lnai.client;

import dev.longnight.lnai.LnAi;
import net.minecraft.client.Minecraft;
import net.minecraft.client.resources.sounds.AbstractTickableSoundInstance;
import net.minecraft.client.resources.sounds.SoundInstance;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * 關卡配樂：伺服器用 /lnhud music 指定曲目（cue），這裡負責淡入淡出與循環。
 * 換曲時舊曲淡出、新曲淡入；同一首重複指定（例如全隊陣亡後重來）不會從頭播。
 * 音量跟著玩家的「音樂」音量設定；播放期間關掉原版的背景音樂。
 */
@Mod.EventBusSubscriber(modid = LnAi.MODID, value = Dist.CLIENT)
public final class MusicPlayer {
    private MusicPlayer() {}

    private static Track current;
    private static Track fading;

    /** cue 空字串 = 停止；fade = 淡入淡出幾 tick */
    public static void play(String cue, int fade) {
        Minecraft mc = Minecraft.getInstance();
        if (current != null && current.cue.equals(cue)) return;
        if (current != null) {
            if (fading != null) mc.getSoundManager().stop(fading);
            fading = current;
            fading.fadeTo(0, fade);
            current = null;
        }
        if (cue.isEmpty()) return;
        ResourceLocation rl = new ResourceLocation(LnAi.MODID, "music." + cue);
        if (mc.getSoundManager().getSoundEvent(rl) == null) return;
        current = new Track(cue, SoundEvent.createVariableRangeEvent(rl));
        current.fadeTo(1, fade);
        mc.getMusicManager().stopPlaying();
        mc.getSoundManager().play(current);
        com.mojang.logging.LogUtils.getLogger().info("[lnai] music {} (fade {})", cue, fade);
    }

    @SubscribeEvent
    public static void tick(TickEvent.ClientTickEvent e) {
        if (e.phase != TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null) { current = null; fading = null; return; }
        if (current != null) {
            mc.getMusicManager().stopPlaying();   // 原版背景音樂不要跟關卡配樂疊在一起
            if (!mc.getSoundManager().isActive(current) && current.age > 40) {   // 被音效系統停掉（例如重載資源）就重新播
                Track t = new Track(current.cue, current.ev);
                t.vol = current.vol;
                t.target = current.target;
                current = t;
                mc.getSoundManager().play(current);
            }
        }
        if (fading != null && fading.isStopped()) fading = null;
    }

    static final class Track extends AbstractTickableSoundInstance {
        final String cue;
        final SoundEvent ev;
        float vol = 0, target = 1, step = 1;
        int age = 0;

        Track(String cue, SoundEvent ev) {
            super(ev, SoundSource.MUSIC, SoundInstance.createUnseededRandom());
            this.cue = cue;
            this.ev = ev;
            this.looping = true;
            this.delay = 0;
            this.relative = true;
            this.attenuation = SoundInstance.Attenuation.NONE;
            this.volume = 0.0001f;
        }

        void fadeTo(float t, int ticks) {
            target = t;
            step = ticks <= 0 ? 1 : Math.max(0.002f, Math.abs(t - vol) / ticks);
        }

        @Override
        public boolean canStartSilent() { return true; }

        @Override
        public void tick() {
            age++;
            if (vol < target) vol = Math.min(target, vol + step);
            else if (vol > target) vol = Math.max(target, vol - step);
            volume = Math.max(0.0001f, vol);
            if (target == 0 && vol <= 0) stop();
        }
    }
}
