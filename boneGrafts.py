from PyQt6.QtWidgets import (
    QComboBox, QLineEdit
)
from baseDialog import AddDialog, EditDialog, RemoveDialog
from baseInventory import Inventory
from baseItem import Item

class BoneGraft(Item):
    def __init__(self, brand, type_, particulate, granule_size, amount, sn, ref, lot, expiry, qty):
        super().__init__(brand,ref, lot, expiry, qty)
        self.type_ = type_
        self.particulate = particulate
        self.granule_size = granule_size
        self.amount = amount
        self.sn = sn

class AddBoneGraftDialog(AddDialog):
    def __init__(self, parent=None, title="Add Bone Graft"):
        super().__init__(parent, title)

    def get_data(self):
        def get_val(widget):
            if isinstance(widget, QComboBox):
                return widget.currentText().strip()
            else:
                return widget.text().strip()
            
        brand=self.brand_input.currentText().strip()
        type_=get_val(self.type_input)
        particulate=get_val(self.particulate_input)
        granule_size=get_val(self.granule_size_input)
        amount=get_val(self.amount_input)
        ref=self.ref_input.text().strip()
        lot=self.lot_input.text().strip()
        sn=self.sn_input.text().strip()
        expiry=self.expiry_input.text().strip()
        qty=self.qty_input.text().strip()

        # Validate inputs, raising exceptions as needed
        expiry_date, qty = self.validate_inputs(
            {
                "brand": brand,
                "type_": type_,
                "particulate": particulate,
                "granule_size": granule_size,
                "amount": amount,
                "sn": sn,
                "ref": ref,
                "lot": lot,
                "expiry": expiry,
                "qty": qty
            },
            expiry,
            qty
        )
        
        return BoneGraft(
            brand=brand,
            type_=type_,
            particulate=particulate,
            granule_size=granule_size,
            amount=amount,
            sn=sn,
            ref=ref,
            lot=lot,
            expiry=expiry_date.strftime("%Y-%m-%d"),
            qty=qty
        )
    
    def _add_dialog_body_widgets(self):
        self._brand_list = ["creos"]
        self._refresh_brand_items()
        self.brand_input.setCurrentText("creos")
        self.brand_input.currentTextChanged.connect(self._set_dynamic_type_widget)
        self.type_input = None
        self.particulate_input = None
        self.granule_size_input = None
        self.amount_input = None
        self.sn_input = QLineEdit()
        
        # Add widgets to layout
        self.layout_.addRow("Brand", self.brand_input)
        self._set_dynamic_type_widget() # Adds type, platform, width, height widgets
        self.layout_.addRow("SN", self.sn_input)
        self.layout_.addRow("REF", self.ref_input)
        self.layout_.addRow("LOT", self.lot_input)
        self.layout_.addRow("Expiry (YYYY-MM-DD)", self.expiry_input)
        self.layout_.addRow("Qty", self.qty_input)

    def _set_dynamic_type_widget(self):
        self.type_input.deleteLater() if self.type_input else None
        # Add new widgets based on selection
        match self.brand_input.currentText():
            case "creos":
                self.type_input = QComboBox()
                self.type_input.addItems([
                    "Allograft",
                    "Xenograft"
                ])
                self.type_input.setCurrentText("Allograft")
                self.type_input.currentTextChanged.connect(self._set_dynamic_particulate_widget)
                self.type_input.currentTextChanged.connect(self._set_dynamic_sn_widget)
            case _:
                self.type_input = QLineEdit()
        # Remove any existing row at this position before inserting to avoid
        # accumulating rows (which causes the dialog to grow each time)
        if self.layout_.rowCount() > 1:
            self.layout_.removeRow(1)
        self.layout_.insertRow(1, "Type", self.type_input)
        self._set_dynamic_particulate_widget()
        self._set_dynamic_sn_widget
    
    def _set_dynamic_particulate_widget(self):
        self.particulate_input.deleteLater() if self.particulate_input else None
        if isinstance(self.type_input, QComboBox):
            match self.type_input.currentText():
                case "Allograft":
                    self.particulate_input = QComboBox()
                    self.particulate_input.addItems([
                        "Corticocancellous",
                        "Demineralized cortical",
                        "Min/demin cortical",
                        "Mineralized cancellous",
                        "Mineralized cortical"
                    ])
                    self.particulate_input.setCurrentText("Corticocancellous")
                    self.particulate_input.currentTextChanged.connect(self._set_dynamic_granule_size_widget)
                case "Xenograft":
                    self.particulate_input = QComboBox()
                    self.particulate_input.addItems(["N/A"])
                    self.particulate_input.setCurrentText("N/A")
                    self.particulate_input.setDisabled(True)
                    self.particulate_input.currentTextChanged.connect(self._set_dynamic_granule_size_widget)
                case _:
                    self.particulate_input = QLineEdit()
        else:
            self.particulate_input = QLineEdit()
        # Ensure we don't duplicate the platform row
        if self.layout_.rowCount() > 2:
            self.layout_.removeRow(2)
        self.layout_.insertRow(2, "Platform", self.particulate_input)
        self._set_dynamic_granule_size_widget()
    
    def _set_dynamic_granule_size_widget(self):
        self.granule_size_input.deleteLater() if self.granule_size_input else None
        # Add new widgets based on selection
        if isinstance(self.type_input, QComboBox):
            match self.type_input.currentText():
                case "Allograft":
                    if isinstance(self.particulate_input, QComboBox):
                        match self.particulate_input.currentText():
                            case "Corticocancellous":
                                self.granule_size_input = QComboBox()
                                self.granule_size_input.addItems([
                                    "0.25-1.00 mm",
                                    "0.50-1.00 mm"
                                ])
                                self.granule_size_input.setCurrentText("0.25-1.00 mm")
                                self.granule_size_input.currentTextChanged.connect(self._set_dynamic_amount_widget)
                            case "Demineralized cortical":
                                self.granule_size_input = QComboBox()
                                self.granule_size_input.addItems([
                                    "0.125-0.850 mm",
                                    "0.50-1.00 mm"
                                ])
                                self.granule_size_input.setCurrentText("0.125-0.850 mm")
                                self.granule_size_input.currentTextChanged.connect(self._set_dynamic_amount_widget)
                            case "Min/demin cortical":
                                self.granule_size_input = QComboBox()
                                self.granule_size_input.addItems([
                                    "0.25-1.00 mm"
                                ])
                                self.granule_size_input.setCurrentText("0.25-1.00 mm")
                                self.granule_size_input.currentTextChanged.connect(self._set_dynamic_amount_widget)
                            case "Mineralized cancellous":
                                self.granule_size_input = QComboBox()
                                self.granule_size_input.addItems([
                                    "0.25-1.00 mm",
                                    "0.50-1.00 mm"
                                ])
                                self.granule_size_input.setCurrentText("0.25-1.00 mm")
                                self.granule_size_input.currentTextChanged.connect(self._set_dynamic_amount_widget)
                            case "Mineralized cortical":
                                self.granule_size_input = QComboBox()
                                self.granule_size_input.addItems([
                                    "0.125-0.850 mm",
                                    "0.25-1.00 mm",
                                    "0.50-1.00 mm"
                                ])
                                self.granule_size_input.setCurrentText("0.125-0.850 mm")
                                self.granule_size_input.currentTextChanged.connect(self._set_dynamic_amount_widget)
                            case _:
                                self.granule_size_input = QLineEdit()
                    else:
                        self.amount_input = QLineEdit()
                case "Xenograft":
                    self.granule_size_input = QComboBox()
                    self.granule_size_input.addItems([
                        "0.2-1.0 mm",
                        "1.0-2.0 mm"
                    ])
                    self.granule_size_input.setCurrentText("0.2-1.0 mm")
                    self.granule_size_input.currentTextChanged.connect(self._set_dynamic_amount_widget)
                case _:
                    self.granule_size_input = QLineEdit()
        else:
            self.granule_size_input = QLineEdit()
        # Ensure single width row only
        if self.layout_.rowCount() > 3:
            self.layout_.removeRow(3)
        self.layout_.insertRow(3, "Width", self.granule_size_input)
        self._set_dynamic_amount_widget()

    def _set_dynamic_amount_widget(self):
        self.amount_input.deleteLater() if self.amount_input else None
        # Add new widgets based on selection
        if isinstance(self.type_input, QComboBox):
            match self.type_input.currentText():
                case "Allograft":
                    if isinstance(self.particulate_input, QComboBox):
                        match self.particulate_input.currentText():
                            case (
                                "Corticocancellous" |
                                "Demineralized cortical" |
                                "Mineralized cancellous" |
                                "Mineralized cortical"
                            ):
                                self.amount_input = QComboBox()
                                self.amount_input.addItems(["0.25 cc", "0.5 cc", "1 cc", "2 cc"])
                                self.amount_input.setCurrentText("0.25 cc")
                            case "Min/demin cortical":
                                self.amount_input = QComboBox()
                                self.amount_input.addItems(["0.5 cc", "1 cc", "2 cc"])
                                self.amount_input.setCurrentText("0.5 cc")
                            case _:
                                self.amount_input = QLineEdit()
                    else:
                        self.amount_input = QLineEdit()
                case "Xenograft":
                    self.amount_input = QComboBox()
                    self.amount_input.addItems(["0.25 g", "0.5 g", "1 g", "2 g"])
                    self.amount_input.setCurrentText("0.25 g")
                case _:
                    self.amount_input = QLineEdit()
        else:
            self.amount_input = QLineEdit()
        # Ensure we don't add multiple height rows
        if self.layout_.rowCount() > 4:
            self.layout_.removeRow(4)
        self.layout_.insertRow(4, "Height", self.amount_input)
    
    def _set_dynamic_sn_widget(self):
        if isinstance(self.type_input, QComboBox):
            match self.type_input.currentText():
                case "Allograft":
                    self.sn_input.setText("")
                    self.sn_input.setDisabled(False)
                case "Xenograft" | "Synthetic":
                    self.sn_input.setText("N/A")
                    self.sn_input.setDisabled(True)
                case _:
                    self.sn_input.setText("")
                    self.sn_input.setDisabled(False)

class EditBoneGraftDialog(EditDialog):
    def __init__(
            self,
            inventory: list[BoneGraft],
            brand: str,
            type_: str,
            particulate: str,
            granule_size: str,
            amount: str,
            sn: str,
            parent=None
        ):
        super().__init__(
            inventory=inventory,
            ItemClass=BoneGraft,
            header_labels=["Brand", "Type", "Particulate", "Granule Size", "Amount", "SN", "REF", "LOT", "Expiry", "Qty in Stock"],
            attributes=["brand", "type_", "particulate", "granule_size", "amount", "sn", "ref", "lot", "expiry", "qty"],
            parent=parent,
            title="Edit Bone Graft",
            title_label=f"Edit from {brand} - {type_} (Particulate: {particulate}, Granule Size: {granule_size}, Amount: {amount}, SN: {sn})",
            item_name="bone graft"
        )

class RemoveBoneGraftDialog(RemoveDialog):
    def __init__(
            self, 
            inventory: list[BoneGraft],
            brand: str,
            type_: str,
            particulate: str,
            granule_size: str,
            amount: str,
            parent=None,
            *args,
            **kwargs
        ):
        super().__init__(
            inventory=inventory,
            header_labels=["SN", "REF", "LOT", "Expiry", "Qty in Stock"], 
            attributes=["sn", "ref", "lot", "expiry", "qty"], 
            parent=parent,
            title="Remove Bone Graft",
            title_label=f"Remove from {brand} - {type_} (Particulate: {particulate}, Granule Size: {granule_size}, Amount: {amount})",
            item_name="bone graft"
        )

class BoneGraftInventory(Inventory):
    def __init__(
            self,
            inventory_file: str,
            low_quantity: int=2,
            days_from_expiry: int=180
            ):
        super().__init__(
            inventory_file=inventory_file,
            ItemClass=BoneGraft,
            AddDialogClass=AddBoneGraftDialog,
            EditDialogClass=EditBoneGraftDialog,
            RemoveDialogClass=RemoveBoneGraftDialog,
            header_labels=[
                "Brand", "Type", "Particulate", "Granule Size", "Amount"
            ],
            attributes=[
                "brand", "type_", "particulate", "granule_size", "amount", "sn"
            ],
            item_name="bone graft",
            low_quantity=low_quantity,
            days_from_expiry=days_from_expiry
        )