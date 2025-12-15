from datetime import datetime
from typing import Tuple
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QComboBox, QFormLayout, QInputDialog, QVBoxLayout, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QSpinBox, QMessageBox
)
from baseItem import Item, EditItem, RemovalItem
from exceptions import AllFieldsRequiredError, InvalidDateError, InvalidQuantityError

def _check_all_fields_filled(fields: dict) -> None:
    # Helper to check all fields are filled
    if not all(value.strip() for value in fields.values()):
        raise AllFieldsRequiredError("All fields are required.")
        
def _check_expiry_date(expiry: str) -> datetime:
    # Helper to validate expiry date format
    try:
        return datetime.strptime(expiry, "%Y-%m-%d")
    except ValueError:
        raise InvalidDateError("Expiry must be YYYY-MM-DD")
    
def _check_quantity(qty: str) -> int:
    # Helper to validate quantity is an integer
    try:
        return int(qty)
    except ValueError:
        raise InvalidQuantityError("Quantity must be a number")

class AddDialog(QDialog):
    def __init__(self, parent=None, title="Add Item"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.layout_ = QFormLayout(self)

        self.brand_input = QComboBox()
        self._brand_list = []
        self.brand_input.currentIndexChanged.connect(self._check_add_brand)
        self.expiry_input = QLineEdit()
        self.qty_input = QLineEdit()
        self.ref_input = QLineEdit()
        self.lot_input = QLineEdit()
        self._add_dialog_body_widgets()
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout_.addWidget(self.button_box)

    def get_data(self) -> Item:
        """Gather data from inputs and return Item instance"""            
        brand=self.brand_input.currentText().strip()
        expiry=self.expiry_input.text().strip()
        qty=self.qty_input.text().strip()
        ref=self.ref_input.text().strip()
        lot=self.lot_input.text().strip()

        # Validate inputs, raising exceptions as needed
        expiry_date, qty = self.validate_inputs(
            {
                "brand": brand,
                "expiry": expiry,
                "qty": qty,
                "ref": ref,
                "lot": lot
            },
            expiry,
            qty
        )

        return Item(
            brand=brand,
            expiry=expiry_date.strftime("%Y-%m-%d"),
            qty=qty,
            ref=ref,
            lot=lot
        )

    @staticmethod
    def validate_inputs(
        fields: dict[str, str],
        expiry: str,
        qty: str
    ) -> Tuple[datetime, int]:
        """Static method to validate inputs, raising exceptions as needed."""
        _check_all_fields_filled(fields)
        expiry_date = _check_expiry_date(expiry)
        qty = _check_quantity(qty)
        return expiry_date, qty

    def _add_dialog_body_widgets(self):
        # Initialize dialog, to be overridden by subclasses
        self.layout_.addRow("Brand", self.brand_input)
        self.layout_.addRow("REF", self.ref_input)
        self.layout_.addRow("LOT", self.lot_input)
        self.layout_.addRow("Expiry (YYYY-MM-DD)", self.expiry_input)
        self.layout_.addRow("Qty", self.qty_input)

    def _refresh_brand_items(self):
        # Helper to refresh dropdown with brands + 'Add another brand...'
        self.brand_input.clear()
        brands_sorted = sorted(self._brand_list)
        self.brand_input.addItems(brands_sorted + ["Add another brand..."])

    def _check_add_brand(self):
        # Check if 'Add another brand...' selected
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

class EditDialog(QDialog):
    def __init__(
                self,
                inventory: list[Item],
                ItemClass: type[Item],
                header_labels: list[str], 
                attributes: list[str], 
                parent=None,
                title: str = "Edit Item",
                title_label: str = "Edit Item",
                item_name: str = "item"
            ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setGeometry(300, 300, 700, 400)

        self.inventory = inventory
        self.ItemClass = ItemClass
        self.header_labels = header_labels
        self.attributes = attributes
        self.item_name = item_name

        layout = QVBoxLayout(self)
        title_label = QLabel(title_label)
        layout.addWidget(title_label)

        # Table with editable columns
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.header_labels))
        self.table.setHorizontalHeaderLabels(self.header_labels)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Populate table with matching items
        for item in self.inventory:
            row = self.table.rowCount()
            self.table.insertRow(row)

            for i, attribute in enumerate(self.attributes):
                self.table.setItem(row, i, QTableWidgetItem(str(getattr(item, attribute))))

        # Allow editing in the table
        self.table.setEditTriggers(QTableWidget.EditTrigger.AllEditTriggers)
        layout.addWidget(self.table)

        # OK / Cancel
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.on_ok_clicked)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def on_ok_clicked(self):
        """Validate edits, show confirmation, and accept if confirmed."""
        edits: list[tuple[EditItem, Item]] = []

        for row, original_item in enumerate(self.inventory):
            new = {}
            for col, attribute in enumerate(self.attributes):
                new_value = self.table.item(row, col).text().strip() if self.table.item(row, col) else ""
                new[attribute] = new_value

            # Basic validation
            _check_all_fields_filled(new)
            new["expiry"] = _check_expiry_date(new.get("expiry")).strftime("%Y-%m-%d")
            new["qty"] = _check_quantity(new.get("qty"))

            new_item = self.ItemClass(**new)
            edits.append((EditItem(original_item, row), new_item))

        # Confirmation
        confirmation_text = f"You have made the following edits to {self.item_name}s:\n\n"
        for (o, n) in edits:
            original_line = ", ".join(f"{h}: {getattr(o.item, a)}" for h, a in zip(self.header_labels, self.attributes))
            new_line = ", ".join(f"{h}: {getattr(n, a)}" for h, a in zip(self.header_labels, self.attributes))
            confirmation_text += (
                f"Original: {original_line}\n"
                f" -> New: {new_line}\n\n"
            )
        confirmation_text += "Do you want to apply these changes?"

        reply = QMessageBox.question(
            self,
            "Confirm Edits",
            confirmation_text,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.edits = edits
            self.accept()

    def get_edits(self) -> list[tuple[EditItem, Item]]:
        return getattr(self, 'edits', [])

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
        
        # Confirmation dialog
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