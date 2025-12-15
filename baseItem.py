class BaseItem:
    def __init__(self, ref, lot, expiry):
        self.ref = ref
        self.lot = lot
        self.expiry = expiry

class Item(BaseItem):
    """Generic item class to be inherited from."""
    def __init__(self, brand, ref, lot, expiry, qty: int):
        super().__init__(ref, lot, expiry)
        self.brand = brand
        self.qty = qty

class EditItem:
    """Class to be used by the EditDialog class when editing an item in an inventory."""
    def __init__(self, item: Item, inventory_index: int):
        self.item = item
        self.inventory_index = inventory_index

class RemovalItem(BaseItem):
    """Class to be used by the RemoveDialog class when removing quantity from an item in an inventory."""
    def __init__(self, ref, lot, expiry, remove_qty: int, inventory_index: int):
        super().__init__(ref, lot, expiry)
        self.remove_qty = remove_qty
        self.inventory_index = inventory_index