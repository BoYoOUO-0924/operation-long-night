package dev.longnight.lnai.client;

import dev.longnight.lnai.LnAi;
import net.minecraft.client.Minecraft;
import net.minecraft.client.resources.sounds.AbstractTickableSoundInstance;
import net.minecraft.client.resources.sounds.SoundInstance;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * 關卡配樂與環境音：伺服器用 /lnhud music、/lnhud ambient 指定（cue），這裡負責淡入淡出與循環。
 * 換曲時舊曲淡出、新曲淡入；同一首重複指定（例如全隊陣亡後重來）不會從頭播。
 * 配樂跟著「音樂」音量、播放期間關掉原版背景音樂；環境音跟著「環境」音量，進到室內（頭上有屋頂）會變小聲。
 */
@Mod.EventBusSubscriber(modid = LnAi.MODID, value = Dist.CLIENT)
public final class MusicPlayer {
    private MusicPlayer() {}

    static final Channel MUSIC = new Channel("music.", SoundSource.MUSIC, false);
    static final Channel AMBIENT = new Channel("sfx.", SoundSource.AMBIENT, true);

    /** cue 空字串 = 停止；「amb:」開頭的是環境音；fade = 淡入淡出幾 tick */
    public static void play(String cue, int fade) {
        if (cue.startsWith("tint:")) ScreenTint.set(cue.substring(5));
        else if (cue.startsWith("amb:")) AMBIENT.play(cue.substring(4), fade);
        else MUSIC.play(cue, fade);
    }

    @SubscribeEvent
    public static void tick(TickEvent.ClientTickEvent e) {
        if (e.phase != TickEvent.Phase.END) return;
        ScreenTint.tick();
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null) { MUSIC.reset(); AMBIENT.reset(); return; }
        if (MUSIC.current != null) mc.getMusicManager().stopPlaying();   // 原版背景音樂不要跟關卡配樂疊在一起
        MUSIC.tick(mc);
        AMBIENT.tick(mc);
    }

    static final class Channel {
        final String prefix;
        final SoundSource source;
        final boolean muffleIndoors;
        Track current, fading;

        Channel(String prefix, SoundSource source, boolean muffleIndoors) {
            this.prefix = prefix;
            this.source = source;
            this.muffleIndoors = muffleIndoors;
        }

        void reset() { current = null; fading = null; }

        void play(String cue, int fade) {
            Minecraft mc = Minecraft.getInstance();
            if (current != null && current.cue.equals(cue)) return;
            if (current != null) {
                if (fading != null) mc.getSoundManager().stop(fading);
                fading = current;
                fading.fadeTo(0, fade);
                current = null;
            }
            if (cue.isEmpty()) return;
            ResourceLocation rl = new ResourceLocation(LnAi.MODID, prefix + cue);
            if (mc.getSoundManager().getSoundEvent(rl) == null) return;
            current = new Track(this, cue, SoundEvent.createVariableRangeEvent(rl));
            current.fadeTo(1, fade);
            if (source == SoundSource.MUSIC) mc.getMusicManager().stopPlaying();
            mc.getSoundManager().play(current);
            com.mojang.logging.LogUtils.getLogger().info("[lnai] {} {} (fade {})", source == SoundSource.MUSIC ? "music" : "ambient", cue, fade);
        }

        void tick(Minecraft mc) {
            if (current != null && !mc.getSoundManager().isActive(current) && current.age > 40) {   // 被音效系統停掉（例如重載資源）就重新播
                Track t = new Track(this, current.cue, current.ev);
                t.vol = current.vol;
                t.target = current.target;
                current = t;
                mc.getSoundManager().play(current);
            }
            if (fading != null && fading.isStopped()) fading = null;
        }
    }

    static final class Track extends AbstractTickableSoundInstance {
        final Channel ch;
        final String cue;
        final SoundEvent ev;
        float vol = 0, target = 1, step = 1, room = 1;
        int age = 0;

        Track(Channel ch, String cue, SoundEvent ev) {
            super(ev, ch.source, SoundInstance.createUnseededRandom());
            this.ch = ch;
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
            if (ch.muffleIndoors) {
                Minecraft mc = Minecraft.getInstance();
                float want = 1;
                if (mc.player != null && mc.level != null
                        && !mc.level.canSeeSky(BlockPos.containing(mc.player.getEyePosition()))) want = 0.35f;
                room += (want - room) * 0.05f;   // 進出室內約 1 秒平滑過渡
            }
            volume = Math.max(0.0001f, vol * room);
            if (target == 0 && vol <= 0) stop();
        }
    }
}
