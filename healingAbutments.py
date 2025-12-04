from PyQt6.QtWidgets import (
    QComboBox, QLabel, QLineEdit
)
from baseDialog import AddDialog

class AddHealingAbutmentDialog(AddDialog):
    def __init__(self, parent=None, title="Add Healing Abutment"):
        super().__init__(parent, title)

        self._brand_list = ["Nobel", "Straumann"]
        self._refresh_brand_items()
        self.brand_input.setCurrentText("Nobel")

        self._layout.addRow("Brand", self.brand_input)
        self.type_input = QLineEdit()
        self._layout.addRow("Type", self.type_input)
        self.platform_input = QLineEdit()
        self._layout.addRow("Platform", self.platform_input)
        self.width_input = QLineEdit()
        self._layout.addRow("Width", self.width_input)
        self.height_input = QLineEdit()
        self._layout.addRow("Height", self.height_input)
        self.expiry_input = QLineEdit()
        self._layout.addRow("Expiry (YYYY-MM-DD)", self.expiry_input)
        self.qty_input = QLineEdit()
        self._layout.addRow("Qty", self.qty_input)
        self.ref_input = QLineEdit()
        self._layout.addRow("REF", self.ref_input)
        self.lot_input = QLineEdit()
        self._layout.addRow("LOT", self.lot_input)

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