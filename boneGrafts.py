from PyQt6.QtWidgets import (
    QComboBox, QLabel, QLineEdit
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

    def _add_dialog_body_widgets(self):
        # Initialize dialog
        self.layout_.addRow("Brand", self.brand_input)
        self.type_input = QLineEdit()
        self.layout_.addRow("Type", self.type_input)
        self.particulate_input = QLineEdit()
        self.layout_.addRow("Particulate", self.particulate_input)
        self.granule_size_input = QLineEdit()
        self.layout_.addRow("Granule Size", self.granule_size_input)
        self.amount_input = QLineEdit()
        self.layout_.addRow("Amount", self.amount_input)
        self.sn_input = QLineEdit()
        self.layout_.addRow("SN", self.sn_input)
        self.ref_input = QLineEdit()
        self.layout_.addRow("REF", self.ref_input)
        self.lot_input = QLineEdit()
        self.layout_.addRow("LOT", self.lot_input)
        self.expiry_input = QLineEdit()
        self.layout_.addRow("Expiry (YYYY-MM-DD)", self.expiry_input)
        self.qty_input = QLineEdit()
        self.layout_.addRow("Qty", self.qty_input)

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
        self._check_all_fields_filled({
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
        })
        expiry_date = self._check_expiry_date(expiry)
        qty = self._check_quantity(qty)

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
            parent=None
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
            inventory_file: str
            ):
        super().__init__(
            inventory_file=inventory_file,
            ItemClass=BoneGraft,
            AddDialogClass=AddBoneGraftDialog,
            EditDialogClass=EditBoneGraftDialog,
            RemoveDialogClass=RemoveBoneGraftDialog,
            header_labels=[
                "Brand", "Type", "Particulate", "Granule Size", "Amount", "SN"
            ],
            attributes=[
                "brand", "type_", "particulate", "granule_size", "amount", "sn"
            ],
            item_name="bone graft"
        )