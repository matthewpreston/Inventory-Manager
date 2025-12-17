from PyQt6.QtWidgets import (
    QComboBox, QLineEdit
)
from baseDialog import AddDialog, EditDialog, RemoveDialog
from baseInventory import Inventory
from baseItem import Item

class Membrane(Item):
    def __init__(self, brand, biologic_type, membrane_type, shape, size, thickness, sn, ref, lot, expiry, qty):
        super().__init__(brand,ref, lot, expiry, qty)
        self.biologic_type = biologic_type
        self.membrane_type = membrane_type
        self.shape = shape
        self.size = size
        self.thickness = thickness
        self.sn = sn

class AddMembraneDialog(AddDialog):
    def __init__(self, parent=None, title="Add Membrane"):
        super().__init__(parent, title)

    def get_data(self):
        def get_val(widget):
            if isinstance(widget, QComboBox):
                return widget.currentText().strip()
            else:
                return widget.text().strip()
            
        brand=self.brand_input.currentText().strip()
        biologic_type=get_val(self.biologic_type_input)
        membrane_type=get_val(self.membrane_type_input)
        shape=get_val(self.shape_input)
        size=get_val(self.size_input)
        thickness=get_val(self.thickness_input)
        ref=self.ref_input.text().strip()
        lot=self.lot_input.text().strip()
        sn=self.sn_input.text().strip()
        expiry=self.expiry_input.text().strip()
        qty=self.qty_input.text().strip()

        # Validate inputs, raising exceptions as needed
        expiry_date, qty = self.validate_inputs(
            {
                "brand": brand,
                "biologic_type": biologic_type,
                "membrane_type": membrane_type,
                "shape": shape,
                "size": size,
                "thickness": thickness,
                "sn": sn,
                "ref": ref,
                "lot": lot,
                "expiry": expiry,
                "qty": qty
            },
            expiry,
            qty
        )
        
        return Membrane(
            brand=brand,
            biologic_type=biologic_type,
            membrane_type=membrane_type,
            shape=shape,
            size=size,
            thickness=thickness,
            sn=sn,
            ref=ref,
            lot=lot,
            expiry=expiry_date.strftime("%Y-%m-%d"),
            qty=qty
        )
    
    def _add_dialog_body_widgets(self):
        self._brand_list = ["creos", "Osteogenics"]
        self._refresh_brand_items()
        self.brand_input.setCurrentText("Osteogenics")
        self.brand_input.currentTextChanged.connect(self._set_dynamic_biologic_type_widget)
        self.biologic_type_input = None
        self.membrane_type_input = None
        self.shape_input = None
        self.size_input = None
        self.thickness_input = None
        self.sn_input = QLineEdit()
        
        # Add widgets to layout
        self.layout_.addRow("Brand", self.brand_input)
        self._set_dynamic_biologic_type_widget()
        self.layout_.addRow("SN", self.sn_input)
        self.layout_.addRow("REF", self.ref_input)
        self.layout_.addRow("LOT", self.lot_input)
        self.layout_.addRow("Expiry (YYYY-MM-DD)", self.expiry_input)
        self.layout_.addRow("Qty", self.qty_input)

    def _set_dynamic_biologic_type_widget(self):
        self.biologic_type_input.deleteLater() if self.biologic_type_input else None
        # Add new widgets based on selection
        match self.brand_input.currentText():
            case "creos":
                self.biologic_type_input = QComboBox()
                self.biologic_type_input.addItems([
                    "Allograft",
                    "Xenograft"
                ])
                self.biologic_type_input.setCurrentText("Allograft")
                self.biologic_type_input.currentTextChanged.connect(self._set_dynamic_membrane_type_widget)
                self.biologic_type_input.currentTextChanged.connect(self._set_dynamic_sn_widget)
            case "Osteogenics":
                self.biologic_type_input = QComboBox()
                self.biologic_type_input.addItems([
                    "Xenograft",
                    "Synthetic"
                ])
                self.biologic_type_input.setCurrentText("Xenograft")
                self.biologic_type_input.currentTextChanged.connect(self._set_dynamic_membrane_type_widget)
                self.biologic_type_input.currentTextChanged.connect(self._set_dynamic_sn_widget)
            case _:
                self.biologic_type_input = QLineEdit()
        # Remove any existing row at this position before inserting to avoid
        # accumulating rows (which causes the dialog to grow each time)
        if self.layout_.rowCount() > 1:
            self.layout_.removeRow(1)
        self.layout_.insertRow(1, "Biologic Type", self.biologic_type_input)
        self._set_dynamic_membrane_type_widget()
        self._set_dynamic_sn_widget()
    
    def _set_dynamic_membrane_type_widget(self):
        self.membrane_type_input.deleteLater() if self.membrane_type_input else None
        if isinstance(self.biologic_type_input, QComboBox):
            match self.biologic_type_input.currentText():
                case "Allograft":
                    self.membrane_type_input = QComboBox()
                    self.membrane_type_input.addItems(["Pericardium"])
                    self.membrane_type_input.setCurrentText("Pericardium")
                    self.membrane_type_input.setDisabled(True)
                    self.membrane_type_input.currentTextChanged.connect(self._set_dynamic_shape_widget)
                case "Xenograft":
                    self.membrane_type_input = QComboBox()
                    self.membrane_type_input.addItems(["Collagen"])
                    self.membrane_type_input.setCurrentText("Collagen")
                    self.membrane_type_input.setDisabled(True)
                    self.membrane_type_input.currentTextChanged.connect(self._set_dynamic_shape_widget)
                case "Synthetic":
                    self.membrane_type_input = QComboBox()
                    self.membrane_type_input.addItems(["d-PTFE", "Ti-reinforced PTFE"])
                    self.membrane_type_input.setCurrentText("d-PTFE")
                    self.membrane_type_input.currentTextChanged.connect(self._set_dynamic_shape_widget)
                case _:
                    self.membrane_type_input = QLineEdit()
        else:
            self.membrane_type_input = QLineEdit()
        # Ensure we don't duplicate the platform row
        if self.layout_.rowCount() > 2:
            self.layout_.removeRow(2)
        self.layout_.insertRow(2, "Membrane Type", self.membrane_type_input)
        self._set_dynamic_shape_widget()
    
    def _set_dynamic_shape_widget(self):
        self.shape_input.deleteLater() if self.shape_input else None
        # Add new widgets based on selection
        if isinstance(self.membrane_type_input, QComboBox):
            match self.membrane_type_input.currentText():
                case "Pericardium" | "Collagen" | "d-PTFE":
                    self.shape_input = QComboBox()
                    self.shape_input.addItems(["Rectangular"])
                    self.shape_input.setCurrentText("Rectangular")
                    self.shape_input.setDisabled(True)
                    self.shape_input.currentTextChanged.connect(self._set_dynamic_size_widget)
                case "Ti-reinforced PTFE":
                    self.shape_input = QComboBox()
                    self.shape_input.addItems([
                        "ANL",
                        "ANL30",
                        "AS",
                        "BL",
                        "BLL",
                        "PS",
                        "PST",
                        "PL",
                        "PLT",
                        "XLK",
                        "XL",
                        "ATC",
                        "PTC",
                        "PD",
                        "K2"
                    ])
                    self.shape_input.setCurrentText("ANL")
                    self.shape_input.currentTextChanged.connect(self._set_dynamic_size_widget)
                case _:
                    self.shape_input = QLineEdit()
        else:
            self.shape_input = QLineEdit()
        # Ensure single width row only
        if self.layout_.rowCount() > 3:
            self.layout_.removeRow(3)
        self.layout_.insertRow(3, "Shape", self.shape_input)
        self._set_dynamic_size_widget()

    def _set_dynamic_size_widget(self):
        self.size_input.deleteLater() if self.size_input else None
        # Add new widgets based on selection
        if isinstance(self.membrane_type_input, QComboBox) and isinstance(self.shape_input, QComboBox):
            match self.membrane_type_input.currentText():
                case "Pericardium":
                    self.size_input = QComboBox()
                    self.size_input.addItems([
                        "10 x 10 mm",
                        "15 x 20 mm",
                        "20 x 30 mm"
                    ])
                    self.size_input.setCurrentText("10 x 10 mm")
                    self.size_input.currentTextChanged.connect(self._set_dynamic_thickness_widget)
                case "Collagen":
                    self.size_input = QComboBox()
                    self.size_input.addItems([
                        "15 x 20 mm",
                        "25 x 30 mm",
                        "30 x 40 mm"
                    ])
                    self.size_input.setCurrentText("15 x 20 mm")
                    self.size_input.currentTextChanged.connect(self._set_dynamic_thickness_widget)
                case "d-PTFE":
                    self.size_input = QComboBox()
                    self.size_input.addItems([
                        "12 x 24 mm",
                        "12 x 30 mm",
                        "25 x 30 mm"
                    ])
                    self.size_input.setCurrentText("12 x 24 mm")
                    self.size_input.currentTextChanged.connect(self._set_dynamic_thickness_widget)
                case "Ti-reinforced PTFE":
                    match self.shape_input.currentText():
                        case "ANL":
                            self.size_input = QComboBox()
                            self.size_input.addItems(["12 x 24 mm"])
                            self.size_input.setCurrentText("12 x 24 mm")
                            self.size_input.setDisabled(True)
                            self.size_input.currentTextChanged.connect(self._set_dynamic_thickness_widget)
                        case "ANL30":
                            self.size_input = QComboBox()
                            self.size_input.addItems(["12 x 30 mm"])
                            self.size_input.setCurrentText("12 x 30 mm")
                            self.size_input.setDisabled(True)
                            self.size_input.currentTextChanged.connect(self._set_dynamic_thickness_widget)
                        case "AS":
                            self.size_input = QComboBox()
                            self.size_input.addItems(["14 x 24 mm"])
                            self.size_input.setCurrentText("14 x 24 mm")
                            self.size_input.setDisabled(True)
                            self.size_input.currentTextChanged.connect(self._set_dynamic_thickness_widget)
                        case "BL":
                            self.size_input = QComboBox()
                            self.size_input.addItems(["17 x 25 mm"])
                            self.size_input.setCurrentText("17 x 25 mm")
                            self.size_input.setDisabled(True)
                            self.size_input.currentTextChanged.connect(self._set_dynamic_thickness_widget)
                        case "BLL":
                            self.size_input = QComboBox()
                            self.size_input.addItems(["17 x 30 mm"])
                            self.size_input.setCurrentText("17 x 30 mm")
                            self.size_input.setDisabled(True)
                            self.size_input.currentTextChanged.connect(self._set_dynamic_thickness_widget)
                        case "PS":
                            self.size_input = QComboBox()
                            self.size_input.addItems(["20 x 25 mm"])
                            self.size_input.setCurrentText("20 x 25 mm")
                            self.size_input.setDisabled(True)
                            self.size_input.currentTextChanged.connect(self._set_dynamic_thickness_widget)
                        case "PST":
                            self.size_input = QComboBox()
                            self.size_input.addItems(["36 x 25 mm"])
                            self.size_input.setCurrentText("36 x 25 mm")
                            self.size_input.setDisabled(True)
                            self.size_input.currentTextChanged.connect(self._set_dynamic_thickness_widget)
                        case "PL":
                            self.size_input = QComboBox()
                            self.size_input.addItems(["25 x 30 mm"])
                            self.size_input.setCurrentText("25 x 30 mm")
                            self.size_input.setDisabled(True)
                            self.size_input.currentTextChanged.connect(self._set_dynamic_thickness_widget)
                        case "PLT":
                            self.size_input = QComboBox()
                            self.size_input.addItems(["30 x 41 mm"])
                            self.size_input.setCurrentText("30 x 41 mm")
                            self.size_input.setDisabled(True)
                            self.size_input.currentTextChanged.connect(self._set_dynamic_thickness_widget)
                        case "XLK":
                            self.size_input = QComboBox()
                            self.size_input.addItems(["30 x 40 mm"])
                            self.size_input.setCurrentText("30 x 40 mm")
                            self.size_input.setDisabled(True)
                            self.size_input.currentTextChanged.connect(self._set_dynamic_thickness_widget)
                        case "XL":
                            self.size_input = QComboBox()
                            self.size_input.addItems(["30 x 40 mm"])
                            self.size_input.setCurrentText("30 x 40 mm")
                            self.size_input.setDisabled(True)
                            self.size_input.currentTextChanged.connect(self._set_dynamic_thickness_widget)
                        case "ATC":
                            self.size_input = QComboBox()
                            self.size_input.addItems(["24 x 38 mm"])
                            self.size_input.setCurrentText("24 x 38 mm")
                            self.size_input.setDisabled(True)
                            self.size_input.currentTextChanged.connect(self._set_dynamic_thickness_widget)
                        case "PTC":
                            self.size_input = QComboBox()
                            self.size_input.addItems(["38 x 38 mm"])
                            self.size_input.setCurrentText("38 x 38 mm")
                            self.size_input.setDisabled(True)
                            self.size_input.currentTextChanged.connect(self._set_dynamic_thickness_widget)
                        case "PD":
                            self.size_input = QComboBox()
                            self.size_input.addItems(["38 x 38 mm"])
                            self.size_input.setCurrentText("38 x 38 mm")
                            self.size_input.setDisabled(True)
                            self.size_input.currentTextChanged.connect(self._set_dynamic_thickness_widget)
                        case "K2":
                            self.size_input = QComboBox()
                            self.size_input.addItems(["40 x 50 mm"])
                            self.size_input.setCurrentText("40 x 50 mm")
                            self.size_input.setDisabled(True)
                            self.size_input.currentTextChanged.connect(self._set_dynamic_thickness_widget)
                        case _:
                            self.size_input = QLineEdit()
                case _:
                    self.size_input = QLineEdit()
        else:
            self.size_input = QLineEdit()
        # Ensure single width row only
        if self.layout_.rowCount() > 4:
            self.layout_.removeRow(4)
        self.layout_.insertRow(4, "Size", self.size_input)
        self._set_dynamic_thickness_widget()

    def _set_dynamic_thickness_widget(self):
        self.thickness_input.deleteLater() if self.thickness_input else None
        # Add new widgets based on selection
        if isinstance(self.membrane_type_input, QComboBox) and isinstance(self.shape_input, QComboBox):
            match self.membrane_type_input.currentText():
                case "Pericardium" | "Collagen" | "d-PTFE":
                    self.thickness_input = QComboBox()
                    self.thickness_input.addItems(["N/A"])
                    self.thickness_input.setCurrentText("N/A")
                    self.thickness_input.setDisabled(True)
                case "Ti-reinforced PTFE":
                    match self.shape_input.currentText():
                        case (
                            "ANL" |
                            "AS" |
                            "BL" |
                            "BLL" |
                            "PS" |
                            "PST" |
                            "PL" |
                            "PLT" |
                            "XLK" |
                            "XL" |
                            "ATC" |
                            "PTC" |
                            "PD" |
                            "K2"
                        ):
                            self.thickness_input = QComboBox()
                            self.thickness_input.addItems(["150 um", "250 um"])
                            self.thickness_input.setCurrentText("150 um")
                        case "ANL30":
                            self.thickness_input = QComboBox()
                            self.thickness_input.addItems(["250 um"])
                            self.thickness_input.setCurrentText("250 um")
                            self.thickness_input.setDisabled(True)
                        case _:
                            self.thickness_input = QLineEdit()
                case _:
                    self.thickness_input = QLineEdit()
        else:
            self.thickness_input = QLineEdit()
        # Ensure we don't add multiple height rows
        if self.layout_.rowCount() > 5:
            self.layout_.removeRow(5)
        self.layout_.insertRow(5, "Thickness", self.thickness_input)

    def _set_dynamic_sn_widget(self):
        if isinstance(self.biologic_type_input, QComboBox):
            match self.biologic_type_input.currentText():
                case "Allograft":
                    self.sn_input.setText("")
                    self.sn_input.setDisabled(False)
                case "Xenograft" | "Synthetic":
                    self.sn_input.setText("N/A")
                    self.sn_input.setDisabled(True)
                case _:
                    self.sn_input.setText("")
                    self.sn_input.setDisabled(False)

class EditMembraneDialog(EditDialog):
    def __init__(
            self,
            inventory: list[Membrane],
            brand: str,
            biologic_type: str,
            membrane_type: str,
            shape: str,
            size: str,
            thickness: str,
            sn: str,
            parent=None
        ):
        super().__init__(
            inventory=inventory,
            ItemClass=Membrane,
            header_labels=["Brand", "Biologic Type", "Membrane Type", "Shape", "Size", "Thickness", "SN", "REF", "LOT", "Expiry", "Qty in Stock"],
            attributes=["brand", "biologic_type", "membrane_type", "shape", "size", "thickness", "sn", "ref", "lot", "expiry", "qty"],
            parent=parent,
            title="Edit Membrane",
            title_label=f"Edit from {brand} {biologic_type} {membrane_type} {shape} {size} {thickness} SN: {sn}",
            item_name="membrane"
        )

class RemoveMembraneDialog(RemoveDialog):
    def __init__(
            self, 
            inventory: list[Membrane],
            brand: str,
            biologic_type: str,
            membrane_type: str,
            shape: str,
            size: str,
            thickness: str,
            parent=None,
            *args,
            **kwargs
        ):
        super().__init__(
            inventory=inventory,
            header_labels=["SN", "REF", "LOT", "Expiry", "Qty in Stock"], 
            attributes=["sn", "ref", "lot", "expiry", "qty"], 
            parent=parent,
            title="Remove Membrane",
            title_label=f"Remove from {brand} {biologic_type} {membrane_type} {shape} {size} {thickness}",
            item_name="membrane"
        )

class MembraneInventory(Inventory):
    def __init__(
            self,
            inventory_file: str,
            low_quantity: int=2,
            days_from_expiry: int=180
            ):
        super().__init__(
            inventory_file=inventory_file,
            ItemClass=Membrane,
            AddDialogClass=AddMembraneDialog,
            EditDialogClass=EditMembraneDialog,
            RemoveDialogClass=RemoveMembraneDialog,
            header_labels=[
                "Brand", "Biologic Type", "Membrane Type", "Shape", "Size", "Thickness", "SN"
            ],
            attributes=[
                "brand", "biologic_type", "membrane_type", "shape", "size", "thickness", "sn"
            ],
            item_name="membrane",
            low_quantity=low_quantity,
            days_from_expiry=days_from_expiry
        )