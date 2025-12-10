from email import header
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QComboBox, QFormLayout, QInputDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QSpinBox, QMessageBox
)

from baseItem import Item, RemovalItem

class AddDialog(QDialog):
    def __init__(self, parent=None, title="Add Item"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.layout_ = QFormLayout(self)

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
        self.layout_.addWidget(self.button_box)

    def get_data(self):
        pass

class RemoveDialog(QDialog):
    def __init__(
                self, 
                inventory: list[Item], 
                header_labels: list[str], 
                attributes: list[str], 
                parent=None, 
                title="Remove Item", 
                title_label="Remove Item",
                item_name="item"
            ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setGeometry(300, 300, 700, 400)
        
        self.inventory = inventory
        self.header_labels = header_labels
        self.attributes = attributes
        self.item_name = item_name

        layout = QVBoxLayout(self)
        
        title_label = QLabel(title_label)
        layout.addWidget(title_label)
        
        # Table to display items
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.header_labels) + 1)  # Extra column for spinbox
        self.table.setHorizontalHeaderLabels(self.header_labels + ["Remove Qty"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Populate table with matching items
        for item in self.inventory:
            row = self.table.rowCount()
            self.table.insertRow(row)

            for i, attribute in enumerate(self.attributes):
                self.table.setItem(row, i, QTableWidgetItem(str(getattr(item, attribute))))

            # Add spinbox for remove quantity
            spinbox = QSpinBox()
            spinbox.setMinimum(0)
            spinbox.setMaximum(item.qty)
            spinbox.setValue(0)
            self.table.setCellWidget(row, len(self.header_labels), spinbox)

        layout.addWidget(self.table)
        
        # OK and Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.on_ok_clicked)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def on_ok_clicked(self):
        """Gather removal selections and show confirmation dialog"""
        removals = []
        
        for row, item in enumerate(self.inventory):
            spinbox = self.table.cellWidget(row, len(self.header_labels))
            remove_qty = spinbox.value()
            
            if remove_qty > 0:
                removals.append(RemovalItem(
                    ref=item.ref,
                    lot=item.lot,
                    expiry=item.expiry,
                    remove_qty=remove_qty,
                    inventory_index=self.inventory.index(item)
                ))
        
        if not removals:
            QMessageBox.information(self, "No Selection", f"Please select at least one {self.item_name} to remove.")
            return
        
        # Show confirmation dialog
        self.show_confirmation(removals)
    
    def show_confirmation(self, removals: list[RemovalItem]):
        """Show confirmation dialog with removal details"""
        confirmation_text = f"You have selected the following {self.item_name}s to remove:\n\n"
        
        for removal in removals:
            confirmation_text += (
                f"REF: {removal.ref}, LOT: {removal.lot}, "
                f"Expiry: {removal.expiry}\n"
                f"  Remove Qty: {removal.remove_qty}\n\n"
            )
        
        confirmation_text += "\nDo you want to proceed with the removal?"
        
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            confirmation_text,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.removals = removals
            self.accept()
        # If No, stay in dialog

    def get_removals(self) -> list[RemovalItem]:
        """Return list of removal operations"""
        return getattr(self, 'removals', [])