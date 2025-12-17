from PyQt6.QtWidgets import (
    QComboBox, QLineEdit
)
from baseDialog import AddDialog, EditDialog, RemoveDialog
from baseInventory import Inventory
from baseItem import Item

class TemporaryAbutment(Item):
    def __init__(self, brand, engagement, platform, collar_height, height, ref, lot, expiry, qty):
        super().__init__(brand, ref, lot, expiry, qty)
        self.engagement = engagement
        self.platform = platform
        self.collar_height = collar_height
        self.height = height

class AddTemporaryAbutmentDialog(AddDialog):
    def __init__(self, parent=None, title="Add Temporary Abutment"):
        super().__init__(parent, title)

    def get_data(self):
        def get_val(widget):
            if isinstance(widget, QComboBox):
                return widget.currentText().strip()
            else:
                return widget.text().strip()
            
        brand=self.brand_input.currentText().strip()
        engagement=get_val(self.engagement_input)
        platform=get_val(self.platform_input)
        collar_height=get_val(self.collar_height_input)
        height=get_val(self.height_input)
        ref=self.ref_input.text().strip()
        lot=self.lot_input.text().strip()
        expiry=self.expiry_input.text().strip()
        qty=self.qty_input.text().strip()

        # Validate inputs, raising exceptions as needed
        expiry_date, qty = self.validate_inputs(
            {
                "brand": brand,
                "engagement": engagement,
                "platform": platform,
                "collar_height": collar_height,
                "height": height,
                "ref": ref,
                "lot": lot,
                "expiry": expiry,
                "qty": qty
            },
            expiry,
            qty
        )

        return TemporaryAbutment(
            brand=brand,
            engagement=engagement,
            platform=platform,
            collar_height=collar_height,
            height=height,
            ref=ref,
            lot=lot,
            expiry=expiry_date.strftime("%Y-%m-%d"),
            qty=qty
        )
    
    def _add_dialog_body_widgets(self):
        self._brand_list = ["Nobel", "Straumann"]
        self._refresh_brand_items()
        self.brand_input.setCurrentText("Nobel")
        self.brand_input.currentTextChanged.connect(self._set_dynamic_engagement_widget)
        self.engagement_input = None
        self.platform_input = None
        self.collar_height_input = None
        self.height_input = None
        
        # Add widgets to layout
        self.layout_.addRow("Brand", self.brand_input)
        self._set_dynamic_engagement_widget()
        self.layout_.addRow("REF", self.ref_input)
        self.layout_.addRow("LOT", self.lot_input)
        self.layout_.addRow("Expiry (YYYY-MM-DD)", self.expiry_input)
        self.layout_.addRow("Qty", self.qty_input)

    def _set_dynamic_engagement_widget(self):
        self.engagement_input.deleteLater() if self.engagement_input else None
        # Add new widgets based on selection
        match self.brand_input.currentText():
            case "Nobel":
                self.engagement_input = QComboBox()
                self.engagement_input.addItems([
                    "Snap Engaging",
                    "Snap Multi-unit",
                    "Engaging",
                    "Non-engaging"
                ])
                self.engagement_input.setCurrentText("Snap Engaging")
                self.engagement_input.currentTextChanged.connect(self._set_dynamic_platform_widget)
            case _:
                self.engagement_input = QLineEdit()
        # Remove any existing row at this position before inserting to avoid
        # accumulating rows (which causes the dialog to grow each time)
        if self.layout_.rowCount() > 1:
            self.layout_.removeRow(1)
        self.layout_.insertRow(1, "Engagement", self.engagement_input)
        self._set_dynamic_platform_widget()
    
    def _set_dynamic_platform_widget(self):
        self.platform_input.deleteLater() if self.platform_input else None
        if isinstance(self.engagement_input, QComboBox):
            match self.engagement_input.currentText():
                case "Snap Engaging" | "Non-engaging":
                    self.platform_input = QComboBox()
                    self.platform_input.addItems(["NP", "RP", "WP"])
                    self.platform_input.setCurrentText("NP")
                    self.platform_input.currentTextChanged.connect(self._set_dynamic_collar_height_widget)
                case "Snap Multi-unit":
                    self.platform_input = QComboBox()
                    self.platform_input.addItems(["NP,RP,WP"])
                    self.platform_input.setCurrentText("NP,RP,WP")
                    self.platform_input.currentTextChanged.connect(self._set_dynamic_collar_height_widget)
                case "Engaging":
                    self.platform_input = QComboBox()
                    self.platform_input.addItems(["3.0", "NP", "RP", "WP"])
                    self.platform_input.setCurrentText("3.0")
                    self.platform_input.currentTextChanged.connect(self._set_dynamic_collar_height_widget)
                case _:
                    self.platform_input = QLineEdit()
        else:
            self.platform_input = QLineEdit()
        # Ensure we don't duplicate the platform row
        if self.layout_.rowCount() > 2:
            self.layout_.removeRow(2)
        self.layout_.insertRow(2, "Platform", self.platform_input)
        self._set_dynamic_collar_height_widget()
    
    def _set_dynamic_collar_height_widget(self):
        self.collar_height_input.deleteLater() if self.collar_height_input else None
        # Add new widgets based on selection
        if isinstance(self.platform_input, QComboBox):
            match self.platform_input.currentText():
                case "3.0":
                    self.collar_height_input = QComboBox()
                    self.collar_height_input.addItems(["1.5"])
                    self.collar_height_input.setCurrentText("1.5")
                    self.collar_height_input.currentTextChanged.connect(self._set_dynamic_height_widget)
                case "NP" | "RP":
                    if isinstance(self.engagement_input, QComboBox):
                        match self.engagement_input.currentText():
                            case "Snap Engaging":
                                self.collar_height_input = QComboBox()
                                self.collar_height_input.addItems(["1.5 mm", "3.0 mm"])
                                self.collar_height_input.setCurrentText("1.5")
                                self.collar_height_input.currentTextChanged.connect(self._set_dynamic_height_widget)
                            case "Engaging" | "Non-engaging":
                                self.collar_height_input = QComboBox()
                                self.collar_height_input.addItems(["1.5"])
                                self.collar_height_input.setCurrentText("1.5")
                                self.collar_height_input.currentTextChanged.connect(self._set_dynamic_height_widget)
                            case _:
                                self.collar_height_input = QLineEdit()
                    else:
                        self.collar_height_input = QLineEdit()
                case "WP":
                    self.collar_height_input = QComboBox()
                    self.collar_height_input.addItems(["1.5 mm", "3.0 mm"])
                    self.collar_height_input.setCurrentText("1.5")
                    self.collar_height_input.currentTextChanged.connect(self._set_dynamic_height_widget)
                case "NP,RP,WP":
                    self.collar_height_input = QComboBox()
                    self.collar_height_input.addItems(["N/A"])
                    self.collar_height_input.setCurrentText("N/A")
                    self.collar_height_input.setDisabled(True)
                    self.collar_height_input.currentTextChanged.connect(self._set_dynamic_height_widget)
                case _:
                    self.collar_height_input = QLineEdit()
        else:
            self.collar_height_input = QLineEdit()
        # Ensure single collar height row only
        if self.layout_.rowCount() > 3:
            self.layout_.removeRow(3)
        self.layout_.insertRow(3, "Collar Height", self.collar_height_input)
        self._set_dynamic_height_widget()

    def _set_dynamic_height_widget(self):
        self.height_input.deleteLater() if self.height_input else None
        # Add new widgets based on selection
        if isinstance(self.engagement_input, QComboBox) and isinstance(self.platform_input, QComboBox):
            if self.engagement_input == "Snap Engaging" and self.platform_input == "WP":
                self.height_input = QComboBox()
                self.height_input.addItems(["4 mm"])
                self.height_input.setCurrentText("4 mm")
            elif self.engagement_input == "Engaging" and self.platform_input == "3.0":
                self.height_input = QComboBox()
                self.height_input.addItems(["9 mm"])
                self.height_input.setCurrentText("9 mm")
            else:
                self.height_input = QComboBox()
                self.height_input.addItems(["10 mm"])
                self.height_input.setCurrentText("10 mm")
        else:
            self.height_input = QLineEdit()
        # Ensure we don't add multiple height rows
        if self.layout_.rowCount() > 4:
            self.layout_.removeRow(4)
        self.layout_.insertRow(4, "Height", self.height_input)

class EditTemporaryAbutmentDialog(EditDialog):
    def __init__(
            self,
            inventory: list[TemporaryAbutment],
            brand: str,
            engagement: str,
            platform: str,
            collar_height: str,
            height: str,
            parent=None
        ):
        super().__init__(
            inventory=inventory,
            ItemClass=TemporaryAbutment,
            header_labels=["Brand", "Engagement", "Platform", "Collar Height", "Height", "REF", "LOT", "Expiry", "Qty in Stock"],
            attributes=["brand", "engagement", "platform", "collar_height", "height", "ref", "lot", "expiry", "qty"],
            parent=parent,
            title="Edit Temporary Abutment",
            title_label=f"Edit from {brand} - {engagement} (Platform: {platform}, Size: {collar_height}x{height})",
            item_name="temporary abutment"
        )

class RemoveTemporaryAbutmentDialog(RemoveDialog):
    def __init__(
            self, 
            inventory: list[TemporaryAbutment],
            brand: str,
            engagement: str,
            platform: str,
            collar_height: str,
            height: str,
            parent=None
        ):
        super().__init__(
            inventory=inventory,
            header_labels=["REF", "LOT", "Expiry", "Qty in Stock"], 
            attributes=["ref", "lot", "expiry", "qty"], 
            parent=parent, 
            title="Remove Temporary Abutment", 
            title_label=f"Remove from {brand} - {engagement} (Platform: {platform}, Size: {collar_height}x{height})",
            item_name="temporary abutment"
        )

class TemporaryAbutmentInventory(Inventory):
    def __init__(
            self,
            inventory_file: str,
            low_quantity: int=2,
            days_from_expiry: int=180
        ):
        super().__init__(
            inventory_file=inventory_file,
            ItemClass=TemporaryAbutment,
            AddDialogClass=AddTemporaryAbutmentDialog,
            EditDialogClass=EditTemporaryAbutmentDialog,
            RemoveDialogClass=RemoveTemporaryAbutmentDialog,
            header_labels=[
                "Brand", "Engagement", "Platform", "Collar Height", "Height"
            ],
            attributes=[
                "brand", "engagement", "platform", "collar_height", "height"
            ],
            item_name="temporary abutment",
            low_quantity=low_quantity,
            days_from_expiry=days_from_expiry
        )