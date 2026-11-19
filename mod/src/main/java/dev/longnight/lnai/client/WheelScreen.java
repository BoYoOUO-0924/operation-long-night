package dev.longnight.lnai.client;

import dev.longnight.lnai.Gear;
import dev.longnight.lnai.Net;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.ItemStack;

/** 長按 4／5 的選擇輪盤：滑鼠往哪個方向就選哪個，放開按鍵（或點左鍵）確認。 */
public class WheelScreen extends Screen {
    private final boolean grenade;
    private final int key;
    private final int prevSlot;
    private int hover = -1;

    WheelScreen(boolean grenade, int key, int prevSlot) {
        super(Component.literal(grenade ? "投擲物" : "醫療"));
        this.grenade = grenade;
        this.key = key;
        this.prevSlot = prevSlot;
    }

    @Override
    public boolean isPauseScreen() { return false; }

    int size() { return grenade ? Gear.Grenade.values().length : Gear.Med.values().length; }

    String label(int i) { return grenade ? Gear.Grenade.values()[i].label : Gear.Med.values()[i].label; }

    int count(int i) {
        Inventory inv = Minecraft.getInstance().player.getInventory();
        return grenade ? ClientInput.count(inv, Gear.Grenade.values()[i]) : ClientInput.count(inv, Gear.Med.values()[i]);
    }

    ItemStack icon(int i) {
        return grenade ? new ItemStack(Gear.Grenade.values()[i].item()) : new ItemStack(Gear.Med.values()[i].item());
    }

    /** 選項 i 的中心角度（從正上方順時針排）。 */
    double angle(int i) { return -Math.PI / 2 + i * 2 * Math.PI / size(); }

    @Override
    public void render(GuiGraphics g, int mx, int my, float pt) {
        int cx = width / 2, cy = height / 2, r = 62;
        double dx = mx - cx, dy = my - cy;
        hover = -1;
        if (dx * dx + dy * dy > 18 * 18) {
            double a = Math.atan2(dy, dx), best = 9;
            for (int i = 0; i < size(); i++) {
                double d = Math.abs(Math.atan2(Math.sin(a - angle(i)), Math.cos(a - angle(i))));
                if (d < best) { best = d; hover = i; }
            }
        }
        g.fill(cx - 20, cy - 10, cx + 20, cy + 10, 0x99141A22);
        Hud.text(g, grenade ? "投擲物" : "醫療", cx, cy - 4, 0xFFC8C8C8, true);
        for (int i = 0; i < size(); i++) {
            int x = cx + (int) (Math.cos(angle(i)) * r), y = cy + (int) (Math.sin(angle(i)) * r);
            boolean on = i == hover, cur = grenade && Gear.Grenade.values()[i] == ClientState.grenade;
            int n = count(i);
            g.fill(x - 34, y - 20, x + 34, y + 20, on ? 0xE0141A22 : 0xA0141A22);
            Hud.box(g, x - 34, y - 20, 68, 40, on ? 0xFFFFFFFF : cur ? 0xFFFAC775 : 0x55FFFFFF);
            g.renderItem(icon(i), x - 8, y - 17);
            Hud.text(g, label(i), x, y + 1, n > 0 ? 0xFFFFFFFF : 0xFF777777, true);
            Hud.text(g, "×" + n, x, y + 11, n > 0 ? 0xFFC8C8C8 : 0xFF777777, true);
        }
        Hud.text(g, "放開按鍵確認", cx, cy + r + 30, 0xFF9A9A9A, true);
    }

    @Override
    public boolean keyReleased(int keyCode, int scanCode, int mods) {
        if (keyCode == key) { confirm(); return true; }
        return super.keyReleased(keyCode, scanCode, mods);
    }

    @Override
    public boolean mouseClicked(double x, double y, int button) {
        if (button == 0) { confirm(); return true; }
        return super.mouseClicked(x, y, button);
    }

    void confirm() {
        Minecraft mc = Minecraft.getInstance();
        ClientInput.heldKey = -1;
        onClose();
        if (hover < 0 || count(hover) == 0) return;
        if (grenade) {
            ClientState.grenade = Gear.Grenade.values()[hover];
            Net.CH.sendToServer(new Net.Action(Net.Action.GRENADE, hover, prevSlot));
            mc.player.getInventory().selected = Gear.SLOT_GRENADE;
        } else {
            Net.CH.sendToServer(new Net.Action(Net.Action.MED_PICK, hover, prevSlot));
        }
    }
}
