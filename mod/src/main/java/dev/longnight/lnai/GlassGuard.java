package dev.longnight.lnai;

import com.mojang.logging.LogUtils;
import java.util.LinkedHashMap;
import java.util.Map;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.Event;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.registries.ForgeRegistries;
import org.slf4j.Logger;

/**
 * 子彈打玻璃（TaCZ 的 AmmoHitBlockEvent，會打破玻璃）：
 *   大廳（運輸機範圍）內 → 取消，子彈直接消失，玻璃不破；
 *   其他地方 → 照常打破，但先記下原本的方塊，關卡收尾時 `lnglass restore` 全部補回去。
 * TaCZ 不是編譯依賴，所以用反射註冊事件。
 */
final class GlassGuard {
    private GlassGuard() {}

    private static final Logger LOG = LogUtils.getLogger();
    /** 大廳範圍（generators/out/transport_plane.json 的 box） */
    private static final int X1 = -336, Y1 = 270, Z1 = 891, X2 = -268, Y2 = 294, Z2 = 962;
    private static final Map<BlockPos, Saved> BROKEN = new LinkedHashMap<>();

    private record Saved(ResourceKey<Level> dim, BlockState state) {}

    @SuppressWarnings({"unchecked", "rawtypes"})
    static void init() {
        try {
            Class c = Class.forName("com.tacz.guns.api.event.server.AmmoHitBlockEvent");
            var getState = c.getMethod("getState");
            var getHit = c.getMethod("getHitResult");
            var getLevel = c.getMethod("getLevel");
            var getAmmo = c.getMethod("getAmmo");
            MinecraftForge.EVENT_BUS.addListener(EventPriority.HIGH, false, c, (java.util.function.Consumer) ev -> {
                try {
                    Event e = (Event) ev;
                    BlockState st = (BlockState) getState.invoke(e);
                    if (!isGlass(st)) return;
                    Level lv = (Level) getLevel.invoke(e);
                    if (lv.isClientSide) return;
                    BlockPos p = ((BlockHitResult) getHit.invoke(e)).getBlockPos();
                    if (inLobby(p)) {
                        e.setCanceled(true);
                        ((Entity) getAmmo.invoke(e)).discard();
                    } else {
                        BROKEN.putIfAbsent(p.immutable(), new Saved(lv.dimension(), st));
                    }
                } catch (Exception ex) { LOG.warn("[lnai] glass guard: {}", ex.toString()); }
            });
            LOG.info("[lnai] glass guard on");
        } catch (ClassNotFoundException ex) {
            LOG.warn("[lnai] TaCZ AmmoHitBlockEvent not found, glass guard off");
        } catch (Exception ex) { LOG.warn("[lnai] glass guard init failed: {}", ex.toString()); }
    }

    static boolean isGlass(BlockState st) {
        var id = ForgeRegistries.BLOCKS.getKey(st.getBlock());
        return id != null && id.getPath().contains("glass");
    }

    static boolean inLobby(BlockPos p) {
        return p.getX() >= X1 && p.getX() <= X2 && p.getY() >= Y1 && p.getY() <= Y2 && p.getZ() >= Z1 && p.getZ() <= Z2;
    }

    static void register(RegisterCommandsEvent e) {
        e.getDispatcher().register(Commands.literal("lnglass").requires(s -> s.hasPermission(2))
                .then(Commands.literal("restore").executes(c -> {
                    int n = 0;
                    for (Map.Entry<BlockPos, Saved> en : BROKEN.entrySet()) {
                        ServerLevel lv = c.getSource().getServer().getLevel(en.getValue().dim());
                        if (lv == null) continue;
                        if (!lv.getBlockState(en.getKey()).equals(en.getValue().state())) {
                            lv.setBlock(en.getKey(), en.getValue().state(), 2);
                            n++;
                        }
                    }
                    BROKEN.clear();
                    int done = n;
                    c.getSource().sendSuccess(() -> net.minecraft.network.chat.Component.literal("restored " + done + " glass"), false);
                    return n;
                })));
    }
}
