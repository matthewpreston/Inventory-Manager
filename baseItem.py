class Item:
    def __init__(self, brand, ref, lot, expiry, qty: int):
        self.brand = brand
        self.ref = ref
        self.lot = lot
        self.expiry = expiry
        self.qty = qty

class RemovalItem:
    def __init__(self, ref, lot, expiry, remove_qty: int, inventory_index: int):
        self.ref = ref
        self.lot = lot
        self.expiry = expiry
        self.remove_qty = remove_qty
        self.inventory_index = inventory_index