import csv
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QDialog
)
from baseDialog import AddDialog, RemoveDialog
from baseItem import Item
from exceptions import AllFieldsRequiredError, InvalidDateError, InvalidQuantityError

class Inventory:
    def __init__(
            self,
            inventory_file: str,
            ItemClass: type[Item],
            AddDialogClass: AddDialog,
            RemoveDialogClass: RemoveDialog,
            header_labels: list[str],
            attributes: list[str],
            item_name: str="Item"
        ):
        self.inventory_file = inventory_file
        self.ItemClass = ItemClass
        self.AddDialogClass = AddDialogClass
        self.RemoveDialogClass = RemoveDialogClass
        self.header_labels = header_labels
        self.attributes = attributes
        if len(header_labels) != len(attributes):
            raise ValueError("header_labels and attribute_labels must have the same length.")
        self.item_name = item_name.lower()

        self.inventory: list[Item] = []
        self.selected_row = None

        self.widget = QWidget()
        layout = QVBoxLayout()
                
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton(f"Add {self.item_name.title()}")
        self.add_btn.clicked.connect(self.add_item)
        self.remove_btn = QPushButton(f"Remove {self.item_name.title()}")
        self.remove_btn.clicked.connect(self.remove_item)
        self.remove_btn.setEnabled(False)
        self.save_btn = QPushButton("Save All")
        self.save_btn.clicked.connect(self.save_data)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(len(header_labels) + 4)  # Additional columns for total qty, recent expiry, recent expiry qty, status
        self.table.setHorizontalHeaderLabels(header_labels + [
            "Total Qty", "Most Recent Expiry", "Most Recent Expiry Qty", "Status"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.table)
        self.widget.setLayout(layout)

    def on_selection_changed(self):
        """Enable/disable remove button based on table selection"""
        selected_items = self.table.selectedItems()
        if selected_items:
            self.selected_row = selected_items[0].row()
            self.remove_btn.setEnabled(True)
        else:
            self.selected_row = None
            self.remove_btn.setEnabled(False)

    def add_item(self):
        dialog: AddDialog = self.AddDialogClass(self.widget)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                item = dialog.get_data()
            except (AllFieldsRequiredError, InvalidDateError, InvalidQuantityError) as e:
                QMessageBox.warning(self.widget, "Error", str(e))
                return
            self.inventory.append(item)
            self.update_table()
    
    def update_table(self):
        self.table.setRowCount(0)
        now = datetime.now()
        sorted_condensed_inventory = self._get_sorted_condensed_inventory()

        for item in sorted_condensed_inventory:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for attr in self.attributes:
                self.table.setItem(row, self.attributes.index(attr), QTableWidgetItem(str(item[attr])))
            self.table.setItem(row, len(self.attributes), QTableWidgetItem(str(item["total_qty"])))
            self.table.setItem(row, len(self.attributes) + 1, QTableWidgetItem(item["most_recent_expiry"]))
            self.table.setItem(row, len(self.attributes) + 2, QTableWidgetItem(str(item["most_recent_expiry_qty"])))

            try:
                expiry_date = datetime.strptime(item["most_recent_expiry"], "%Y-%m-%d")
            except Exception:
                expiry_date = None
            status = ""
            if item["total_qty"] <= 2:
                status = "⚠ Low Stock"
            if expiry_date and (expiry_date - now).days < 180:
                if status:
                    status += ", Expiring Soon"
                else:
                    status = "⚠ Expiring Soon"
            self.table.setItem(row, len(self.attributes) + 3, QTableWidgetItem(status))

    def _get_sorted_condensed_inventory(self) -> list[dict]:
        """Groups items by brand, type, platform, width, and length."""
        # Create a dictionary to hold grouped items
        grouped = {}
        for item in self.inventory:
            key = tuple()
            for attr in self.attributes:
                key += (getattr(item, attr),)

            # Create unique groups based on attributes
            if key not in grouped:
                group = {}
                for attr in self.attributes:
                    group[attr] = getattr(item, attr)
                group["total_qty"] = 0
                group["expiries"] = []
                grouped[key] = group

            grouped[key]["total_qty"] += item.qty
            grouped[key]["expiries"].append({"date": item.expiry, "qty": item.qty})

        # Condense the grouped inventory into a list
        condensed = []
        for group in grouped.values():
            expiries_sorted = sorted(group["expiries"], key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"), reverse=True)
            most_recent_expiry = expiries_sorted[0]["date"]
            most_recent_count = sum(e["qty"] for e in expiries_sorted if e["date"] == most_recent_expiry)
            
            condensed_item = {}
            for attr in self.attributes:
                condensed_item[attr] = group[attr]
            condensed_item["total_qty"] = group["total_qty"]
            condensed_item["most_recent_expiry"] = most_recent_expiry
            condensed_item["most_recent_expiry_qty"] = most_recent_count
            condensed.append(condensed_item)
        
        # Sort condensed list based on header labels and most recent expiry
        def key_func(x):
            result = tuple()
            for attr in self.attributes:
                result += (x[attr],)
            return result + (x["most_recent_expiry"],)
        sorted_condensed = sorted(
            condensed,
            key=key_func
        )

        return sorted_condensed
    
    def remove_item(self):
        """Open dialog to remove selected item"""
        if self.selected_row is None:
            QMessageBox.warning(self, "Error", "Please select a row first.")
            return

        # Get stats for selected item
        sorted_condensed_inventory = self._get_sorted_condensed_inventory()
        selected_item = sorted_condensed_inventory[self.selected_row]

        # Get all matching items from inventory
        matching_items = [
            item for item in self.inventory
            if all(
                getattr(item, attr) == selected_item[attr]
                for attr in self.attributes
            )
        ]

        args = {}
        for attr in self.attributes:
            args[attr.lower()] = selected_item[attr.lower()]
        dialog: RemoveDialog = self.RemoveDialogClass(
            matching_items,
            parent=self.widget,
            **args
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            removals = dialog.get_removals()
            
            for removal in removals:
                remove_qty = removal.remove_qty

                matching_item = matching_items[removal.inventory_index]
                # Find the index in the main inventory
                inventory_index = -1
                for inv_item in self.inventory:
                    if (
                            all(
                                getattr(inv_item, attr.lower()) == getattr(matching_item, attr.lower())
                                for attr in self.attributes
                            ) and
                            inv_item.ref == matching_item.ref and
                            inv_item.lot == matching_item.lot and
                            inv_item.expiry == matching_item.expiry
                        ):
                        inventory_index = self.inventory.index(inv_item)
                        break

                if inventory_index == -1:
                    continue  # Should not happen
                if self.inventory[inventory_index].qty > remove_qty:
                    self.inventory[inventory_index].qty -= remove_qty
                else:
                    del self.inventory[inventory_index]
            
            self.update_table()
            QMessageBox.information(self.widget, "Success", f"{len(removals)} {self.item_name}s removed successfully.")

    def save_data(self):
        # Save items to CSV file
        try:
            with open(self.inventory_file, "w", newline="") as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(self.header_labels + ["REF", "LOT", "Expiry", "Qty"])
                for item in self.inventory:
                    writer.writerow(
                        [getattr(item, attr) for attr in self.attributes] +
                        [
                            item.ref,
                            item.lot,
                            item.expiry,
                            item.qty
                        ]
                    )
            QMessageBox.information(self.widget, "Saved", f"{self.item_name.capitalize()}s saved to {self.inventory_file}.")
        except Exception as e:
            QMessageBox.warning(self.widget, "Save Error", f"Failed to save {self.item_name}s: {e}")

    def load_data(self):
        # Load items from CSV file
        try:
            with open(self.inventory_file, "r") as f:
                reader = csv.reader(f)
                for row in reader:
                    # Skip empty rows
                    if not row:
                        continue
                    # Skip header row if present
                    if (
                            row[0].strip().lower() == self.header_labels[0].strip().lower() or
                            (
                                len(row) > len(self.header_labels) and
                                row[len(self.header_labels)].strip().lower() == "expiry"
                            )
                    ):
                        continue
                    # Skip rows with incorrect number of columns
                    if len(row) != len(self.header_labels) + 4:
                        continue
                    args = {}
                    for i, a in enumerate(self.attributes):
                        args[a] = row[i]
                    self.inventory.append(self.ItemClass(
                        **args,
                        ref=row[len(self.header_labels)],
                        lot=row[len(self.header_labels) + 1],
                        expiry=row[len(self.header_labels) + 2],
                        qty=int(row[len(self.header_labels) + 3])
                    ))
        except FileNotFoundError:
            QMessageBox.information(self.widget, "Info", f"No existing {self.item_name} inventory file found. A new one will be created upon saving.")
            self.inventory = []
        except Exception as e:
            QMessageBox.warning(self.widget, "Load Error", f"Failed to load {self.item_name}s: {e}")
            QMessageBox.information(self.widget, "Info", f"No existing {self.item_name} inventory file found. A new one will be created upon saving.")
            self.inventory = []