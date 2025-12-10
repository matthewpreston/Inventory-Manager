from PyQt6.QtWidgets import (
    QComboBox, QLabel, QLineEdit
)
from baseDialog import AddDialog, RemoveDialog
from baseItem import Item

class BoneGraft(Item):
    def __init__(self, brand, type_, particulate, granule_size, amount, ref, lot, sn, expiry, qty):
        super().__init__(ref, lot, expiry, qty)
        self.brand = brand
        self.type_ = type_
        self.particulate = particulate
        self.granule_size = granule_size
        self.amount = amount
        self.sn = sn

class AddBoneGraftDialog(AddDialog):
    def __init__(self, parent=None, title="Add Bone Graft"):
        super().__init__(parent, title)

        self._brand_list = ["Nobel", "Straumann"]
        self._refresh_brand_items()
        self.brand_input.setCurrentText("Nobel")

        self.layout_.addRow("Brand", self.brand_input)
        self.type_input = QLineEdit()
        self.layout_.addRow("Type", self.type_input)
        self.particulate_input = QLineEdit()
        self.layout_.addRow("Particulate", self.particulate_input)
        self.granule_size_input = QLineEdit()
        self.layout_.addRow("Granule Size", self.granule_size_input)
        self.amount_input = QLineEdit()
        self.layout_.addRow("Amount", self.amount_input)
        self.expiry_input = QLineEdit()
        self.layout_.addRow("Expiry (YYYY-MM-DD)", self.expiry_input)
        self.qty_input = QLineEdit()
        self.layout_.addRow("Qty", self.qty_input)
        self.ref_input = QLineEdit()
        self.layout_.addRow("REF", self.ref_input)
        self.lot_input = QLineEdit()
        self.layout_.addRow("LOT", self.lot_input)
        self.sn_input = QLineEdit()
        self.layout_.addRow("SN", self.sn_input)

        self._add_button_box()

    def get_data(self):
        return {
            "brand": self.brand_input.currentText().strip(),
            "type": self.type_input.text().strip(),
            "particulate": self.particulate_input.text().strip(),
            "granule_size": self.granule_size_input.text().strip(),
            "amount": self.amount_input.text().strip(),
            "expiry": self.expiry_input.text().strip(),
            "qty": self.qty_input.text().strip(),
            "ref": self.ref_input.text().strip(),
            "lot": self.lot_input.text().strip(),
            "sn": self.sn_input.text().strip(),
        }

class RemoveBoneGraftDialog(RemoveDialog):
    def __init__(
                self, 
                inventory: list[Item], 
                brand: str,
                type_: str,
                particulate: str,
                granule_size: str,
                amount: str,
                parent=None
            ):
        super().__init__(
            inventory, 
            header_labels=["REF", "LOT", "SN", "Expiry", "Qty in Stock"], 
            attributes=["ref", "lot", "sn", "expiry", "qty"], 
            parent=parent, 
            title="Remove Bone Graft", 
            title_label=f"Remove from {brand} - {type_} (Particulate: {particulate}, Granule Size: {granule_size}, Amount: {amount})",
            item_name="bone graft"
        )