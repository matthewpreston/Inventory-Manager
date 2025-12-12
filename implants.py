from PyQt6.QtWidgets import (
    QComboBox, QLabel, QLineEdit
)
from baseDialog import AddDialog, RemoveDialog
from baseInventory import Inventory
from baseItem import Item

class Implant(Item):
    def __init__(self, brand, type_, platform, width, length, ref, lot, expiry, qty):
        super().__init__(brand, ref, lot, expiry, qty)
        self.type_ = type_
        self.platform = platform
        self.width = width
        self.length = length

class AddImplantDialog(AddDialog):
    def __init__(self, parent=None, title="Add Implant"):
        super().__init__(parent, title)

    def _add_dialog_body_widgets(self):
        # Initialize dialog
        self._brand_list = ["Nobel", "Straumann"]
        self._refresh_brand_items()
        # Set default and connect change handler so dependent widgets update when brand changes
        self.brand_input.setCurrentText("Nobel")
        # Update dynamic widgets whenever the brand selection changes
        self.brand_input.currentTextChanged.connect(self._on_brand_changed)
        self.layout_.addRow("Brand", self.brand_input)
        self.type_label = QLabel("Type")
        self.type_input = None
        self.platform_label = QLabel("Platform")
        self.platform_input = None
        self.width_label = QLabel("Width")
        self.width_input = None
        self.length_label = QLabel("Length")
        self.length_input = None
        self._set_dynamic_widgets() # Also adds to layout
        self.layout_.addRow("REF", self.ref_input)
        self.layout_.addRow("LOT", self.lot_input)
        self.layout_.addRow("Expiry (YYYY-MM-DD)", self.expiry_input)
        self.layout_.addRow("Qty", self.qty_input)

    def _set_dynamic_widgets(self):
        # Remove existing widgets if present
        self.type_input.deleteLater() if self.type_input else None
        self.platform_input.deleteLater() if self.platform_input else None
        self.width_input.deleteLater() if self.width_input else None
        self.length_input.deleteLater() if self.length_input else None
        # Add new widgets based on selected brand
        brand = self.brand_input.currentText()
        if brand == "Nobel":
            # Type
            self.type_input = QComboBox()
            self.type_input.addItems([
                "NobelParallel TiUltra",
                "NobelActive TiUltra"
            ])
            # Platform
            self.platform_input = QComboBox()
            self.platform_input.addItems(["3.0", "RP", "NP", "WP"])
            # Width
            self.width_input = QComboBox()
            self.width_input.addItems(["3.0", "3.5", "3.75", "4.3", "5.0", "5.5"])
            # Length
            self.length_input = QComboBox()
            self.length_input.addItems(["7.0", "8.5", "10.0", "11.5", "13", "15", "18"])
        else:
            self.type_input = QLineEdit()
            self.platform_input = QLineEdit()
            self.width_input = QLineEdit()
            self.length_input = QLineEdit()
        # Insert in order
        self.layout_.insertRow(1, self.type_label, self.type_input)
        self.layout_.insertRow(2, self.platform_label, self.platform_input)
        self.layout_.insertRow(3, self.width_label, self.width_input)
        self.layout_.insertRow(4, self.length_label, self.length_input)

    def _on_brand_changed(self, new_brand: str):
        """Handler called when the brand combobox text changes.

        Rebuilds the dependent inputs (type/platform/width/length) to match the
        newly selected brand. Kept lightweight: defers to _set_dynamic_widgets().
        """
        # Recreate dynamic widgets based on the new brand selection
        self._set_dynamic_widgets()

    def get_data(self):
        def get_val(widget):
            if isinstance(widget, QComboBox):
                return widget.currentText().strip()
            else:
                return widget.text().strip()
            
        brand=self.brand_input.currentText().strip()
        type_=get_val(self.type_input)
        platform=get_val(self.platform_input)
        width=get_val(self.width_input)
        length=get_val(self.length_input)
        ref=self.ref_input.text().strip()
        lot=self.lot_input.text().strip()
        expiry=self.expiry_input.text().strip()
        qty=self.qty_input.text().strip()

        # Validate inputs, raising exceptions as needed
        self._check_all_fields_filled({
            "brand": brand,
            "type_": type_,
            "platform": platform,
            "width": width,
            "length": length,
            "ref": ref,
            "lot": lot,
            "expiry": expiry,
            "qty": qty
        })
        expiry_date = self._check_expiry_date(expiry)
        qty = self._check_quantity(qty)

        return Implant(
            brand=brand,
            type_=type_,
            platform=platform,
            width=width,
            length=length,
            ref=ref,
            lot=lot,
            expiry=expiry_date.strftime("%Y-%m-%d"),
            qty=qty
        )
    
class RemoveImplantDialog(RemoveDialog):
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
            title="Remove Implant", 
            title_label=f"Remove from {brand} - {type_} (Platform: {platform}, Size: {width}x{length})",
            item_name="implant"
        )

class ImplantInventory(Inventory):
    def __init__(
            self,
            inventory_file: str,
            ItemClass=Implant,
            AddDialogClass=AddImplantDialog,
            RemoveDialogClass=RemoveImplantDialog,
            header_labels=[
                "Brand", "Type", "Platform", "Width", "Length"
            ],
            attribute_labels=[
                "brand", "type_", "platform", "width", "length"
            ],
            item_name="implant"):
        super().__init__(inventory_file, ItemClass, AddDialogClass, RemoveDialogClass, header_labels, attribute_labels, item_name)