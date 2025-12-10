from datetime import datetime
from PyQt6.QtWidgets import (
    QComboBox, QLabel, QLineEdit
)
from baseDialog import AddDialog, RemoveDialog
from baseItem import Item
from exceptions import AllFieldsRequiredError, InvalidDateError, InvalidQuantityError

class Implant(Item):
    def __init__(self, brand, type_, platform, width, length, ref, lot, expiry, qty):
        super().__init__(ref, lot, expiry, qty)
        self.brand = brand
        self.type_ = type_
        self.platform = platform
        self.width = width
        self.length = length

class AddImplantDialog(AddDialog):
    def __init__(self, parent=None, title="Add Implant"):
        super().__init__(parent, title)

        self._brand_list = ["Nobel", "Straumann"]
        self._refresh_brand_items()
        self.brand_input.setCurrentText("Nobel")

        self.layout_.addRow("Brand", self.brand_input)
        self.type_label = QLabel("Type")
        self.type_input = None
        self.platform_label = QLabel("Platform")
        self.platform_input = None
        self.width_label = QLabel("Width")
        self.width_input = None
        self.length_label = QLabel("Length")
        self.length_input = None
        self._set_dynamic_widgets()
        self.expiry_input = QLineEdit()
        self.layout_.addRow("Expiry (YYYY-MM-DD)", self.expiry_input)
        self.qty_input = QLineEdit()
        self.layout_.addRow("Qty", self.qty_input)
        self.ref_input = QLineEdit()
        self.layout_.addRow("REF", self.ref_input)
        self.lot_input = QLineEdit()
        self.layout_.addRow("LOT", self.lot_input)

        self._add_button_box()

    def _set_dynamic_widgets(self):
        # Remove existing widgets if present
        for label, widget in [
            (self.type_label, self.type_input),
            (self.platform_label, self.platform_input),
            (self.width_label, self.width_input),
            (self.length_label, self.length_input)
        ]:
            if widget is not None:
                self.layout_.removeRow(label)
        brand = self.brand_input.currentText()
        # Type
        if brand == "Nobel":
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
        expiry=self.expiry_input.text().strip()
        qty=self.qty_input.text().strip()
        ref=self.ref_input.text().strip()
        lot=self.lot_input.text().strip()

        if not (brand and type_ and platform and width and length and expiry and qty and ref and lot):
            raise AllFieldsRequiredError("All fields are required.")

        try:
            expiry_date = datetime.strptime(expiry, "%Y-%m-%d")
        except ValueError:
            raise InvalidDateError("Expiry must be YYYY-MM-DD")

        try:
            qty = int(qty)
        except ValueError:
            raise InvalidQuantityError("Quantity must be a number")

        return Implant(
            brand=brand,
            type_=type_,
            platform=platform,
            width=width,
            length=length,
            expiry=expiry_date.strftime("%Y-%m-%d"),
            qty=qty,
            ref=ref,
            lot=lot
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