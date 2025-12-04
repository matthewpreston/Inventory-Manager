from PyQt6.QtWidgets import (
    QComboBox, QLabel, QLineEdit
)
from baseDialog import AddDialog

# Dialog for implant input
class AddImplantDialog(AddDialog):
    def __init__(self, parent=None, title="Add Implant"):
        super().__init__(parent, title)

        self._brand_list = ["Nobel", "Straumann"]
        self._refresh_brand_items()
        self.brand_input.setCurrentText("Nobel")

        self._layout.addRow("Brand", self.brand_input)
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
        self._layout.addRow("Expiry (YYYY-MM-DD)", self.expiry_input)
        self.qty_input = QLineEdit()
        self._layout.addRow("Qty", self.qty_input)
        self.ref_input = QLineEdit()
        self._layout.addRow("REF", self.ref_input)
        self.lot_input = QLineEdit()
        self._layout.addRow("LOT", self.lot_input)

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
                self._layout.removeRow(label)
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
        self._layout.insertRow(1, self.type_label, self.type_input)
        self._layout.insertRow(2, self.platform_label, self.platform_input)
        self._layout.insertRow(3, self.width_label, self.width_input)
        self._layout.insertRow(4, self.length_label, self.length_input)

    def get_data(self):
        def get_val(widget):
            if isinstance(widget, QComboBox):
                return widget.currentText().strip()
            else:
                return widget.text().strip()
        return {
            "brand": self.brand_input.currentText().strip(),
            "type": get_val(self.type_input),
            "platform": get_val(self.platform_input),
            "width": get_val(self.width_input),
            "length": get_val(self.length_input),
            "expiry": self.expiry_input.text().strip(),
            "qty": self.qty_input.text().strip(),
            "ref": self.ref_input.text().strip(),
            "lot": self.lot_input.text().strip(),
        }