package dev.longnight.lnai;

import java.util.EnumMap;
import java.util.Map;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModItems {
    private ModItems() {}

    public static final DeferredRegister<Item> ITEMS = DeferredRegister.create(ForgeRegistries.ITEMS, LnAi.MODID);
    public static final Map<Gear.Med, RegistryObject<Item>> MEDS = new EnumMap<>(Gear.Med.class);

    static {
        for (Gear.Med m : Gear.Med.values())
            MEDS.put(m, ITEMS.register(m.id, () -> new MedItem(m)));
    }

    /** 右鍵也能使用：交給伺服器的治療流程（會自動計時、可被打斷）。 */
    static final class MedItem extends Item {
        final Gear.Med med;

        MedItem(Gear.Med med) {
            super(new Item.Properties().stacksTo(med == Gear.Med.MEDKIT ? 3 : 8));
            this.med = med;
        }

        @Override
        public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
            ItemStack s = player.getItemInHand(hand);
            if (!level.isClientSide && player instanceof ServerPlayer sp) Heal.start(sp, med, sp.getInventory().selected);
            return InteractionResultHolder.consume(s);
        }
    }
}
