package dev.longnight.lnai.client;

import dev.kosmx.playerAnim.api.layered.IAnimation;
import dev.kosmx.playerAnim.api.layered.KeyframeAnimationPlayer;
import dev.kosmx.playerAnim.api.layered.ModifierLayer;
import dev.kosmx.playerAnim.api.layered.modifier.AbstractFadeModifier;
import dev.kosmx.playerAnim.core.data.KeyframeAnimation;
import dev.kosmx.playerAnim.core.util.Ease;
import dev.kosmx.playerAnim.minecraftApi.PlayerAnimationAccess;
import dev.kosmx.playerAnim.minecraftApi.PlayerAnimationRegistry;
import dev.longnight.lnai.LnAi;
import java.lang.reflect.Field;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.WeakHashMap;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.slf4j.Logger;

/**
 * 角色動作（玩家端）：用 Player Animator 播放 assets/lnai/player_animation/ 裡的動作。
 *
 * TaCZ NPC 是用「假玩家」畫出來的（AutoGunOperatorRenderer.fakePlayerCache：NPC → 假玩家），
 * 動作就掛在那個假玩家身上。假玩家不在世界裡、不會自己更新，所以動作的時間由這裡每 tick 推進。
 * 真的玩家也可以播動作（遊戲會自己推進）。
 */
@Mod.EventBusSubscriber(modid = LnAi.MODID, value = Dist.CLIENT)
public final class NpcAnim {
    private NpcAnim() {}

    private static final Logger LOG = com.mojang.logging.LogUtils.getLogger();
    private static final Map<AbstractClientPlayer, ModifierLayer<IAnimation>> LAYERS = new WeakHashMap<>();
    /** 假玩家還沒建立（NPC 還沒被畫過）時先記著，之後每 tick 再試 */
    private static final Map<Integer, String> PENDING = new HashMap<>();
    private static Field cache;
    private static boolean noCache;

    public static void play(int entityId, String anim) {
        if (!apply(entityId, anim)) PENDING.put(entityId, anim);
    }

    private static boolean apply(int entityId, String anim) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null) return true;
        Entity e = mc.level.getEntity(entityId);
        if (e == null) return false;
        AbstractClientPlayer target = e instanceof AbstractClientPlayer p ? p : fakeOf(e);
        if (target == null) return false;
        ModifierLayer<IAnimation> layer = LAYERS.computeIfAbsent(target, t -> {
            ModifierLayer<IAnimation> l = new ModifierLayer<>();
            PlayerAnimationAccess.getPlayerAnimLayer(t).addAnimLayer(1000, l);
            return l;
        });
        if (anim.isEmpty() || anim.equals("stop")) {
            layer.replaceAnimationWithFade(AbstractFadeModifier.standardFadeIn(5, Ease.INOUTSINE), null);
            return true;
        }
        KeyframeAnimation a = PlayerAnimationRegistry.getAnimation(new ResourceLocation(LnAi.MODID, anim));
        if (a == null) { LOG.warn("[lnai] no animation lnai:{} (have {})", anim, PlayerAnimationRegistry.getModAnimations(LnAi.MODID).keySet()); return true; }
        layer.replaceAnimationWithFade(AbstractFadeModifier.standardFadeIn(4, Ease.INOUTSINE), new KeyframeAnimationPlayer(a));
        return true;
    }

    /** NPC 對應的假玩家（還沒畫過就是 null） */
    @SuppressWarnings("unchecked")
    static AbstractClientPlayer fakeOf(Entity npc) {
        if (noCache) return null;
        try {
            if (cache == null) cache = Class.forName("mod.cdv.tnpc.client.render.AutoGunOperatorRenderer").getField("fakePlayerCache");
            Object v = ((Map<Object, Object>) cache.get(null)).get(npc);
            return v instanceof AbstractClientPlayer p ? p : null;
        } catch (Throwable t) {
            noCache = true;
            LOG.warn("[lnai] TaCZ NPC fake player cache not found: {}", t.toString());
            return null;
        }
    }

    @SubscribeEvent
    public static void onTick(TickEvent.ClientTickEvent e) {
        if (e.phase != TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null) { LAYERS.clear(); PENDING.clear(); return; }
        if (!PENDING.isEmpty()) {
            Iterator<Map.Entry<Integer, String>> it = PENDING.entrySet().iterator();
            while (it.hasNext()) { var p = it.next(); if (apply(p.getKey(), p.getValue())) it.remove(); }
        }
        // 假玩家不會自己更新，動作時間由這裡推進（真的玩家由遊戲推進，不能重複）
        for (var en : LAYERS.entrySet()) if (en.getKey().level() != mc.level || mc.level.getEntity(en.getKey().getId()) != en.getKey()) en.getValue().tick();
    }
}
