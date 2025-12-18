from PyQt6.QtWidgets import (
    QComboBox, QLineEdit
)
from baseDialog import AddDialog, EditDialog, RemoveDialog
from baseInventory import Inventory
from baseItem import Item

class CoverScrew(Item):
    def __init__(self, brand, platform, ref, lot, expiry, qty):
        super().__init__(brand, ref, lot, expiry, qty)
        self.platform = platform

class AddCoverScrewDialog(AddDialog):
    def __init__(self, parent=None, title="Add Cover Screw"):
        super().__init__(parent, title)

    def get_data(self):
        def get_val(widget):
            if isinstance(widget, QComboBox):
                return widget.currentText().strip()
            else:
                return widget.text().strip()
            
        brand=self.brand_input.currentText().strip()
        platform=get_val(self.platform_input)
        ref=self.ref_input.text().strip()
        lot=self.lot_input.text().strip()
        expiry=self.expiry_input.text().strip()
        qty=self.qty_input.text().strip()

        # Validate inputs, raising exceptions as needed
        expiry_date, qty = self.validate_inputs(
            {
                "brand": brand,
                "platform": platform,
                "ref": ref,
                "lot": lot,
                "expiry": expiry,
                "qty": qty
            },
            expiry,
            qty
        )

        return CoverScrew(
            brand=brand,
            platform=platform,
            ref=ref,
            lot=lot,
            expiry=expiry_date.strftime("%Y-%m-%d"),
            qty=qty
        )
    
    def _add_dialog_body_widgets(self):
        self._brand_list = ["Nobel", "Straumann"]
        self._refresh_brand_items()
        self.brand_input.setCurrentText("Nobel")
        self.brand_input.currentTextChanged.connect(self._set_dynamic_platform_widget)
        self.platform_input = None
        
        # Add widgets to layout
        self.layout_.addRow("Brand", self.brand_input)
        self._set_dynamic_platform_widget()
        self.layout_.addRow("REF", self.ref_input)
        self.layout_.addRow("LOT", self.lot_input)
        self.layout_.addRow("Expiry (YYYY-MM-DD)", self.expiry_input)
        self.layout_.addRow("Qty", self.qty_input)

    def _set_dynamic_platform_widget(self):
        self.platform_input.deleteLater() if self.platform_input else None
        if isinstance(self.brand_input, QComboBox):
            match self.brand_input.currentText():
                case "Nobel":
                    self.platform_input = QComboBox()
                    self.platform_input.addItems(["3.0", "NP", "RP", "WP"])
                    self.platform_input.setCurrentText("3.0")
                case _:
                    self.platform_input = QLineEdit()
        else:
            self.platform_input = QLineEdit()
        # Ensure we don't duplicate the platform row
        if self.layout_.rowCount() > 1:
            self.layout_.removeRow(1)
        self.layout_.insertRow(1, "Platform", self.platform_input)

class EditCoverScrewDialog(EditDialog):
    def __init__(
            self,
            inventory: list[CoverScrew],
            brand: str,
            platform: str,
            parent=None
        ):
        super().__init__(
            inventory=inventory,
            ItemClass=CoverScrew,
            header_labels=["Brand", "Platform", "REF", "LOT", "Expiry", "Qty in Stock"],
            attributes=["brand", "platform", "ref", "lot", "expiry", "qty"],
            parent=parent,
            title="Edit Cover Screw",
            title_label=f"Edit from {brand} (Platform: {platform})",
            item_name="cover screw"
        )

class RemoveCoverScrewDialog(RemoveDialog):
    def __init__(
            self, 
            inventory: list[CoverScrew],
            brand: str,
            platform: str,
            parent=None,
            *args,
            **kwargs
        ):
        super().__init__(
            inventory=inventory,
            header_labels=["REF", "LOT", "Expiry", "Qty in Stock"], 
            attributes=["ref", "lot", "expiry", "qty"], 
            parent=parent, 
            title="Remove Cover Screw", 
            title_label=f"Remove from {brand} (Platform: {platform})",
            item_name="cover screw"
        )

class CoverScrewInventory(Inventory):
    def __init__(
            self,
            inventory_file: str,
            low_quantity: int=2,
            days_from_expiry: int=180
        ):
        super().__init__(
            inventory_file=inventory_file,
            ItemClass=CoverScrew,
            AddDialogClass=AddCoverScrewDialog,
            EditDialogClass=EditCoverScrewDialog,
            RemoveDialogClass=RemoveCoverScrewDialog,
            header_labels=[
                "Brand", "Platform"
            ],
            attributes=[
                "brand", "platform"
            ],
            item_name="cover screw",
            low_quantity=low_quantity,
            days_from_expiry=days_from_expiry
        )