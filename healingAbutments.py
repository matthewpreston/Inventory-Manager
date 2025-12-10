from PyQt6.QtWidgets import (
    QComboBox, QLabel, QLineEdit
)
from baseDialog import AddDialog, RemoveDialog
from baseItem import Item

class HealingAbutment(Item):
    def __init__(self, brand, type_, platform, width, height, ref, lot, expiry, qty):
        super().__init__(ref, lot, expiry, qty)
        self.brand = brand
        self.type_ = type_
        self.platform = platform
        self.width = width
        self.height = height

class AddHealingAbutmentDialog(AddDialog):
    def __init__(self, parent=None, title="Add Healing Abutment"):
        super().__init__(parent, title)

        self._brand_list = ["Nobel", "Straumann"]
        self._refresh_brand_items()
        self.brand_input.setCurrentText("Nobel")

        self.layout_.addRow("Brand", self.brand_input)
        self.type_input = QLineEdit()
        self.layout_.addRow("Type", self.type_input)
        self.platform_input = QLineEdit()
        self.layout_.addRow("Platform", self.platform_input)
        self.width_input = QLineEdit()
        self.layout_.addRow("Width", self.width_input)
        self.height_input = QLineEdit()
        self.layout_.addRow("Height", self.height_input)
        self.expiry_input = QLineEdit()
        self.layout_.addRow("Expiry (YYYY-MM-DD)", self.expiry_input)
        self.qty_input = QLineEdit()
        self.layout_.addRow("Qty", self.qty_input)
        self.ref_input = QLineEdit()
        self.layout_.addRow("REF", self.ref_input)
        self.lot_input = QLineEdit()
        self.layout_.addRow("LOT", self.lot_input)

        self._add_button_box()

    def get_data(self):
        return {
            "brand": self.brand_input.currentText().strip(),
            "type": self.type_input.text().strip(),
            "platform": self.platform_input.text().strip(),
            "width": self.width_input.text().strip(),
            "height": self.height_input.text().strip(),
            "expiry": self.expiry_input.text().strip(),
            "qty": self.qty_input.text().strip(),
            "ref": self.ref_input.text().strip(),
            "lot": self.lot_input.text().strip(),
        }

class RemoveHealingAbutmentDialog(RemoveDialog):
    def __init__(
                self, 
                inventory: list[Item],
                brand: str,
                type_: str,
                platform: str,
                width: str,
                length: str,
                parent=None
            ):
        super().__init__(
            inventory, 
            header_labels=["REF", "LOT", "Expiry", "Qty in Stock"], 
            attributes=["ref", "lot", "expiry", "qty"], 
            parent=parent, 
            title="Remove Healing Abutment", 
            title_label=f"Remove from {brand} - {type_} (Platform: {platform}, Size: {width}x{length})",
            item_name="healing abutment"
        )