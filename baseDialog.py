from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QComboBox, QFormLayout, QInputDialog
)

class AddDialog(QDialog):
    def __init__(self, parent=None, title="Add Item"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self._layout = QFormLayout(self)

        self.brand_input = QComboBox()
        self._brand_list = []
        self.brand_input.currentIndexChanged.connect(self._check_add_brand)

    def _refresh_brand_items(self):
        # Helper to refresh dropdown with brands + 'Add another brand...'
        self.brand_input.clear()
        brands_sorted = sorted(self._brand_list)
        self.brand_input.addItems(brands_sorted + ["Add another brand..."])

    def _check_add_brand(self):
        if self.brand_input.currentText() == "Add another brand...":
            text, ok = QInputDialog.getText(self, "Add Brand", "Enter new brand name:")
            if ok and text.strip():
                new_brand = text.strip()
                if new_brand not in self._brand_list:
                    self._brand_list.append(new_brand)
                    self._refresh_brand_items()
                # Set current to new brand
                brands_sorted = sorted(self._brand_list)
                self.brand_input.setCurrentText(new_brand)
            else:
                # Revert to first brand if cancelled
                brands_sorted = sorted(self._brand_list)
                self.brand_input.setCurrentText(brands_sorted[0])
    
    def _add_button_box(self):
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self._layout.addWidget(self.button_box)

    def get_data(self):
        pass