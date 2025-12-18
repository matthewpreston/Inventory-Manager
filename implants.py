from PyQt6.QtWidgets import (
    QComboBox, QLineEdit
)
from baseDialog import AddDialog, EditDialog, RemoveDialog
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
        expiry_date, qty = self.validate_inputs(
            {
                "brand": brand,
                "type_": type_,
                "platform": platform,
                "width": width,
                "length": length,
                "ref": ref,
                "lot": lot,
                "expiry": expiry,
                "qty": qty
            },
            expiry,
            qty
        )

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
    
    def _add_dialog_body_widgets(self):
        """Add specific widgets for adding an Implant."""
        self._brand_list = ["Nobel", "Straumann"]
        self._refresh_brand_items()
        self.brand_input.setCurrentText("Nobel")
        self.brand_input.currentTextChanged.connect(self._set_dynamic_type_widget)
        self.type_input = None
        self.platform_input = None
        self.width_input = None
        self.length_input = None
        
        # Add widgets to layout
        self.layout_.addRow("Brand", self.brand_input)
        self._set_dynamic_type_widget() # Adds type, platform, width, length widgets
        self.layout_.addRow("REF", self.ref_input)
        self.layout_.addRow("LOT", self.lot_input)
        self.layout_.addRow("Expiry (YYYY-MM-DD)", self.expiry_input)
        self.layout_.addRow("Qty", self.qty_input)

    def _set_dynamic_type_widget(self):
        self.type_input.deleteLater() if self.type_input else None
        # Add new widgets based on selection
        match self.brand_input.currentText():
            case "Nobel":
                self.type_input = QComboBox()
                self.type_input.addItems([
                    "NobelActive TiUltra",
                    "NobelParallel TiUltra"
                ])
                self.type_input.setCurrentText("NobelActive TiUltra")
                self.type_input.currentTextChanged.connect(self._set_dynamic_platform_widget)
            case _:
                self.type_input = QLineEdit()
        # Remove any existing row at this position before inserting to avoid
        # accumulating rows (which causes the dialog to grow each time)
        if self.layout_.rowCount() > 1:
            self.layout_.removeRow(1)
        self.layout_.insertRow(1, "Type", self.type_input)
        self._set_dynamic_platform_widget()
    
    def _set_dynamic_platform_widget(self):
        self.platform_input.deleteLater() if self.platform_input else None
        if isinstance(self.type_input, QComboBox):
            match self.type_input.currentText():
                case "NobelActive TiUltra":
                    self.platform_input = QComboBox()
                    self.platform_input.addItems(["3.0", "NP", "RP", "WP"])
                    self.platform_input.setCurrentText("3.0")
                    self.platform_input.currentTextChanged.connect(self._set_dynamic_width_widget)
                case "NobelParallel TiUltra":
                    self.platform_input = QComboBox()
                    self.platform_input.addItems(["NP", "RP", "WP"])
                    self.platform_input.setCurrentText("NP")
                    self.platform_input.currentTextChanged.connect(self._set_dynamic_width_widget)
                case _:
                    self.platform_input = QLineEdit()
        else:
            self.platform_input = QLineEdit()
        # Ensure we don't duplicate the platform row
        if self.layout_.rowCount() > 2:
            self.layout_.removeRow(2)
        self.layout_.insertRow(2, "Platform", self.platform_input)
        self._set_dynamic_width_widget()
    
    def _set_dynamic_width_widget(self):
        self.width_input.deleteLater() if self.width_input else None
        # Add new widgets based on selection
        if isinstance(self.platform_input, QComboBox):
            match self.platform_input.currentText():
                case "3.0":
                    self.width_input = QComboBox()
                    self.width_input.addItems(["3.0"])
                    self.width_input.setCurrentText("3.0")
                    self.width_input.setDisabled(True)
                    self.width_input.currentTextChanged.connect(self._set_dynamic_length_widget)
                case "NP":
                    match self.type_input.currentText():
                        case "NobelActive TiUltra":
                            self.width_input = QComboBox()
                            self.width_input.addItems(["3.5"])
                            self.width_input.setCurrentText("3.5")
                            self.width_input.setDisabled(True)
                            self.width_input.currentTextChanged.connect(self._set_dynamic_length_widget)
                        case "NobelParallel TiUltra":
                            self.width_input = QComboBox()
                            self.width_input.addItems(["3.75"])
                            self.width_input.setCurrentText("3.75")
                            self.width_input.setDisabled(True)
                            self.width_input.currentTextChanged.connect(self._set_dynamic_length_widget)
                        case _:
                            self.width_input = QLineEdit()
                case "RP":
                    self.width_input = QComboBox()
                    self.width_input.addItems(["4.3", "5.0"])
                    self.width_input.setCurrentText("4.3")
                    self.width_input.currentTextChanged.connect(self._set_dynamic_length_widget)
                case "WP":
                    self.width_input = QComboBox()
                    self.width_input.addItems(["5.5"])
                    self.width_input.setCurrentText("5.5")
                    self.width_input.setDisabled(True)
                    self.width_input.currentTextChanged.connect(self._set_dynamic_length_widget)
                case _:
                    self.width_input = QLineEdit()
        else:
            self.width_input = QLineEdit()
        # Ensure single width row only
        if self.layout_.rowCount() > 3:
            self.layout_.removeRow(3)
        self.layout_.insertRow(3, "Width", self.width_input)
        self._set_dynamic_length_widget()

    def _set_dynamic_length_widget(self):
        self.length_input.deleteLater() if self.length_input else None
        # Add new widgets based on selection
        if isinstance(self.width_input, QComboBox):
            match self.width_input.currentText():
                case "3.0":
                    self.length_input = QComboBox()
                    self.length_input.addItems(["10.0", "11.5", "13", "15"])
                    self.length_input.setCurrentText("10.0")
                case "3.5":
                    self.length_input = QComboBox()
                    self.length_input.addItems(["8.5", "10.0", "11.5", "13", "15", "18"])
                    self.length_input.setCurrentText("8.5")
                case "3.75":
                    self.length_input = QComboBox()
                    self.length_input.addItems(["7.0", "8.5", "10.0", "11.5", "13", "15", "18"])
                    self.length_input.setCurrentText("7.0")
                case "4.3" | "5.0":
                    match self.type_input.currentText():
                        case "NobelActive TiUltra":
                            self.length_input = QComboBox()
                            self.length_input.addItems(["8.5", "10.0", "11.5", "13", "15", "18"])
                            self.length_input.setCurrentText("8.5")
                        case "NobelParallel TiUltra":
                            self.length_input = QComboBox()
                            self.length_input.addItems(["7.0", "8.5", "10.0", "11.5", "13", "15", "18"])
                            self.length_input.setCurrentText("7.0")
                        case _:
                            self.length_input = QLineEdit()
                case "5.5":
                    self.length_input = QComboBox()
                    self.length_input.addItems(["7.0", "8.5", "10.0", "11.5", "13", "15"])
                    self.length_input.setCurrentText("7.0")
                case _:
                    self.length_input = QLineEdit()
        else:
            self.length_input = QLineEdit()
        # Ensure we don't add multiple length rows
        if self.layout_.rowCount() > 4:
            self.layout_.removeRow(4)
        self.layout_.insertRow(4, "Length", self.length_input)

class EditImplantDialog(EditDialog):
    def __init__(
            self,
            inventory: list[Implant],
            brand: str,
            type_: str,
            platform: str,
            width: str,
            length: str,
            parent=None
        ):
        super().__init__(
            inventory=inventory,
            ItemClass=Implant,
            header_labels=["Brand", "Type", "Platform", "Width", "Length", "REF", "LOT", "Expiry", "Qty in Stock"],
            attributes=["brand", "type_", "platform", "width", "length", "ref", "lot", "expiry", "qty"],
            parent=parent,
            title="Edit Implant",
            title_label=f"Edit from {brand} - {type_} (Platform: {platform}, Size: {width}x{length})",
            item_name="implant"
        )

class RemoveImplantDialog(RemoveDialog):
    def __init__(
            self, 
            inventory: list[Implant],
            brand: str,
            type_: str,
            platform: str,
            width: str,
            length: str,
            parent=None,
            *args,
            **kwargs
        ):
        super().__init__(
            inventory=inventory,
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
            low_quantity: int=2,
            days_from_expiry: int=180
        ):
        super().__init__(
            inventory_file=inventory_file,
            ItemClass=Implant,
            AddDialogClass=AddImplantDialog,
            EditDialogClass=EditImplantDialog,
            RemoveDialogClass=RemoveImplantDialog,
            header_labels=[
                "Brand", "Type", "Platform", "Width", "Length"
            ],
            attributes=[
                "brand", "type_", "platform", "width", "length"
            ],
            item_name="implant",
            low_quantity=low_quantity,
            days_from_expiry=days_from_expiry
        )