package dev.longnight.lnai.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import dev.longnight.lnai.Gear;
import dev.longnight.lnai.LnAi;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.util.Mth;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderLevelStageEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** 手上拿著投擲物時，畫出拋物線與落點（蓄力越久飛越遠）。 */
@Mod.EventBusSubscriber(modid = LnAi.MODID, value = Dist.CLIENT)
public final class GrenadeArc {
    private GrenadeArc() {}

    @SubscribeEvent
    public static void render(RenderLevelStageEvent e) {
        if (e.getStage() != RenderLevelStageEvent.Stage.AFTER_PARTICLES) return;
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer p = mc.player;
        if (!ClientInput.active(p)) return;
        ItemStack held = p.getMainHandItem();
        Gear.Grenade gr = Gear.Grenade.of(held);
        if (gr == null) return;
        boolean charging = p.isUsingItem() && gr.is(p.getUseItem());
        float power = charging ? gr.power(p.getTicksUsingItem()) : gr.max;
        if (power < 0.05f) power = 0.05f;

        float pt = e.getPartialTick();
        float xRot = p.getViewXRot(pt), yRot = p.getViewYRot(pt);
        double fx = -Mth.sin(yRot * Mth.DEG_TO_RAD) * Mth.cos(xRot * Mth.DEG_TO_RAD);
        double fy = -Mth.sin(xRot * Mth.DEG_TO_RAD);
        double fz = Mth.cos(yRot * Mth.DEG_TO_RAD) * Mth.cos(xRot * Mth.DEG_TO_RAD);
        Vec3 own = p.getDeltaMovement();
        Vec3 vel = new Vec3(fx, fy, fz).normalize().scale(power).add(own.x, p.onGround() ? 0 : own.y, own.z);
        Vec3 pos = p.getPosition(pt).add(0, p.getEyeHeight() - 0.1, 0);

        Vec3 cam = e.getCamera().getPosition();
        PoseStack ps = e.getPoseStack();
        MultiBufferSource.BufferSource buf = mc.renderBuffers().bufferSource();
        VertexConsumer vc = buf.getBuffer(RenderType.lines());
        PoseStack.Pose pose = ps.last();
        int alpha = charging ? 230 : 110;
        Vec3 hit = null;
        for (int i = 0; i < 160; i++) {
            if (!gr.moveFirst) vel = vel.subtract(0, gr.gravity, 0).scale(gr.drag);
            Vec3 next = pos.add(vel);
            BlockHitResult r = p.level().clip(new ClipContext(pos, next, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, p));
            if (r.getType() != HitResult.Type.MISS) next = r.getLocation();
            if (i > 0 || pos.distanceToSqr(next) > 0) line(vc, pose, pos.subtract(cam), next.subtract(cam), 255, 255, 255, alpha);
            if (r.getType() != HitResult.Type.MISS) { hit = next; break; }
            pos = next;
            if (gr.moveFirst) vel = vel.subtract(0, gr.gravity, 0);
        }
        if (hit != null) {
            int[] c = gr == Gear.Grenade.SMOKE ? new int[]{200, 200, 200} : new int[]{240, 80, 70};
            double r = gr == Gear.Grenade.SMOKE ? 3.0 : 2.5;
            Vec3 prev = null;
            for (int i = 0; i <= 24; i++) {
                double a = i * Math.PI * 2 / 24;
                Vec3 q = hit.add(Math.cos(a) * r, 0.05, Math.sin(a) * r).subtract(cam);
                if (prev != null) line(vc, pose, prev, q, c[0], c[1], c[2], alpha);
                prev = q;
            }
        }
        buf.endBatch(RenderType.lines());
    }

    static void line(VertexConsumer vc, PoseStack.Pose pose, Vec3 a, Vec3 b, int r, int g, int bl, int al) {
        Vec3 n = b.subtract(a);
        double len = n.length();
        if (len < 1e-6) return;
        n = n.scale(1 / len);
        vc.vertex(pose.pose(), (float) a.x, (float) a.y, (float) a.z).color(r, g, bl, al).normal(pose.normal(), (float) n.x, (float) n.y, (float) n.z).endVertex();
        vc.vertex(pose.pose(), (float) b.x, (float) b.y, (float) b.z).color(r, g, bl, al).normal(pose.normal(), (float) n.x, (float) n.y, (float) n.z).endVertex();
    }
}
