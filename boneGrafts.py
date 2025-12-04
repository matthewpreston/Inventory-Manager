from PyQt6.QtWidgets import (
    QComboBox, QLabel, QLineEdit
)
from baseDialog import AddDialog

class AddBoneGraftDialog(AddDialog):
    def __init__(self, parent=None, title="Add Bone Graft"):
        super().__init__(parent, title)

        self._brand_list = ["Nobel", "Straumann"]
        self._refresh_brand_items()
        self.brand_input.setCurrentText("Nobel")

        self._layout.addRow("Brand", self.brand_input)
        self.type_input = QLineEdit()
        self._layout.addRow("Type", self.type_input)
        self.particulate_input = QLineEdit()
        self._layout.addRow("Particulate", self.particulate_input)
        self.granule_size_input = QLineEdit()
        self._layout.addRow("Granule Size", self.granule_size_input)
        self.amount_input = QLineEdit()
        self._layout.addRow("Amount", self.amount_input)
        self.expiry_input = QLineEdit()
        self._layout.addRow("Expiry (YYYY-MM-DD)", self.expiry_input)
        self.qty_input = QLineEdit()
        self._layout.addRow("Qty", self.qty_input)
        self.ref_input = QLineEdit()
        self._layout.addRow("REF", self.ref_input)
        self.lot_input = QLineEdit()
        self._layout.addRow("LOT", self.lot_input)
        self.sn_input = QLineEdit()
        self._layout.addRow("SN", self.sn_input)

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