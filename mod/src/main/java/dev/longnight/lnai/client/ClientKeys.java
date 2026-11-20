package dev.longnight.lnai.client;

import dev.longnight.lnai.LnAi;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RegisterKeyMappingsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** 註冊按鍵設定（出現在「控制」選單的「長夜」分類）。 */
@Mod.EventBusSubscriber(modid = LnAi.MODID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.MOD)
public final class ClientKeys {
    private ClientKeys() {}

    @SubscribeEvent
    public static void register(RegisterKeyMappingsEvent e) { e.register(ClientInput.MELEE); e.register(ClientInput.CROUCH); }
}
