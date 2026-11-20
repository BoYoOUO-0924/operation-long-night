package dev.longnight.lnai;

import java.util.function.Supplier;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkEvent;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.PacketDistributor;
import net.minecraftforge.network.simple.SimpleChannel;

/** 玩家端與伺服器之間的訊息。 */
public final class Net {
    private Net() {}

    private static final String VER = "1";
    public static final SimpleChannel CH = NetworkRegistry.newSimpleChannel(
            new ResourceLocation(LnAi.MODID, "main"), () -> VER, VER::equals, VER::equals);

    // ---- 玩家 → 伺服器 ----
    /** kind: 0 = 自動選醫療、1 = 指定醫療（arg = Med 序號）、2 = 裝備投擲物（arg = Grenade 序號）、3 = 快速近戰。prevSlot = 按鍵前手上的欄位。 */
    public record Action(int kind, int arg, int prevSlot) {
        public static final int MED_AUTO = 0, MED_PICK = 1, GRENADE = 2, MELEE = 3;

        void write(FriendlyByteBuf b) { b.writeByte(kind); b.writeByte(arg); b.writeByte(prevSlot); }

        static Action read(FriendlyByteBuf b) { return new Action(b.readByte(), b.readByte(), b.readByte()); }

        void handle(Supplier<NetworkEvent.Context> ctx) {
            ServerPlayer p = ctx.get().getSender();
            if (p != null) Loadout.handle(p, this);
            ctx.get().setPacketHandled(true);
        }
    }

    // ---- 伺服器 → 玩家 ----
    /** 治療進度。med = -1 表示結束；restore = 結束後要切回的欄位（-1 不切）。 */
    public record HealSync(int med, int total, int restore) {
        void write(FriendlyByteBuf b) { b.writeByte(med); b.writeShort(total); b.writeByte(restore); }

        static HealSync read(FriendlyByteBuf b) { return new HealSync(b.readByte(), b.readShort(), b.readByte()); }

        void handle(Supplier<NetworkEvent.Context> ctx) {
            ctx.get().enqueueWork(() -> DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () -> dev.longnight.lnai.client.ClientState.onHeal(this)));
            ctx.get().setPacketHandled(true);
        }
    }

    /** 擊殺通報。mine = 是收到的玩家自己打倒的。 */
    public record Kill(String killer, String role, boolean ally, boolean mine) {
        void write(FriendlyByteBuf b) { b.writeUtf(killer); b.writeUtf(role); b.writeBoolean(ally); b.writeBoolean(mine); }

        static Kill read(FriendlyByteBuf b) { return new Kill(b.readUtf(), b.readUtf(), b.readBoolean(), b.readBoolean()); }

        void handle(Supplier<NetworkEvent.Context> ctx) {
            ctx.get().enqueueWork(() -> DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () -> dev.longnight.lnai.client.ClientState.onKill(this)));
            ctx.get().setPacketHandled(true);
        }
    }

    /** 目前目標文字與導航點。text 空字串 = 清除；hasWp = 是否有導航點。 */
    public record Objective(String text, boolean hasWp, double x, double y, double z) {
        void write(FriendlyByteBuf b) { b.writeUtf(text); b.writeBoolean(hasWp); b.writeDouble(x); b.writeDouble(y); b.writeDouble(z); }

        static Objective read(FriendlyByteBuf b) { return new Objective(b.readUtf(), b.readBoolean(), b.readDouble(), b.readDouble(), b.readDouble()); }

        void handle(Supplier<NetworkEvent.Context> ctx) {
            ctx.get().enqueueWork(() -> DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () -> dev.longnight.lnai.client.ClientState.onObjective(this)));
            ctx.get().setPacketHandled(true);
        }
    }

    /** 過場動畫：json = 整個過場檔（不含伺服器指令）；空字串 = 中止。 */
    public record Cutscene(String json) {
        static final int MAX = 1 << 20;

        void write(FriendlyByteBuf b) { b.writeUtf(json, MAX); }

        static Cutscene read(FriendlyByteBuf b) { return new Cutscene(b.readUtf(MAX)); }

        void handle(Supplier<NetworkEvent.Context> ctx) {
            DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () -> dev.longnight.lnai.client.CutscenePlayer.start(json));
            ctx.get().setPacketHandled(true);
        }
    }

    static void register() {
        int id = 0;
        CH.messageBuilder(Action.class, id++, NetworkDirection.PLAY_TO_SERVER)
                .encoder(Action::write).decoder(Action::read).consumerMainThread((m, c) -> m.handle(c)).add();
        CH.messageBuilder(HealSync.class, id++, NetworkDirection.PLAY_TO_CLIENT)
                .encoder(HealSync::write).decoder(HealSync::read).consumerMainThread((m, c) -> m.handle(c)).add();
        CH.messageBuilder(Kill.class, id++, NetworkDirection.PLAY_TO_CLIENT)
                .encoder(Kill::write).decoder(Kill::read).consumerMainThread((m, c) -> m.handle(c)).add();
        CH.messageBuilder(Objective.class, id++, NetworkDirection.PLAY_TO_CLIENT)
                .encoder(Objective::write).decoder(Objective::read).consumerMainThread((m, c) -> m.handle(c)).add();
        CH.messageBuilder(Cutscene.class, id++, NetworkDirection.PLAY_TO_CLIENT)
                .encoder(Cutscene::write).decoder(Cutscene::read).consumerMainThread((m, c) -> m.handle(c)).add();
    }

    public static void to(ServerPlayer p, Object msg) { CH.send(PacketDistributor.PLAYER.with(() -> p), msg); }
}
