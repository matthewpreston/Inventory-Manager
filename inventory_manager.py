import sys
import csv
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QDialog, QDialogButtonBox, QFormLayout, QComboBox, QInputDialog,
    QSpinBox, QTabWidget
)

IMPLANTS_FILE = "implants.csv"
ABUTMENTS_FILE = "abutments.csv"
BONE_GRAFTS_FILE = "bone_grafts.csv"

# Dialog for implant input
class AddImplantDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Implant")
        self.setModal(True)
        self.layout = QFormLayout(self)

        self.brand_input = QComboBox()
        self._brand_list = ["Nobel", "Straumann"]
        self._refresh_brand_items()
        self.brand_input.setCurrentText("Nobel")
        self.brand_input.currentIndexChanged.connect(self._check_add_brand)

        self.layout.addRow("Brand", self.brand_input)
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
        self.layout.addRow("Expiry (YYYY-MM-DD)", self.expiry_input)
        self.qty_input = QLineEdit()
        self.layout.addRow("Qty", self.qty_input)
        self.ref_input = QLineEdit()
        self.layout.addRow("REF", self.ref_input)
        self.lot_input = QLineEdit()
        self.layout.addRow("LOT", self.lot_input)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def _refresh_brand_items(self):
        # Helper to refresh dropdown with brands + 'Add another brand...'
        self.brand_input.clear()
        brands_sorted = sorted(self._brand_list)
        self.brand_input.addItems(brands_sorted + ["Add another brand..."])

    def _set_dynamic_widgets(self):
        # Remove existing widgets if present
        for label, widget in [
            (self.type_label, self.type_input),
            (self.platform_label, self.platform_input),
            (self.width_label, self.width_input),
            (self.length_label, self.length_input)
        ]:
            if widget is not None:
                self.layout.removeRow(label)
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
        self.layout.insertRow(1, self.type_label, self.type_input)
        self.layout.insertRow(2, self.platform_label, self.platform_input)
        self.layout.insertRow(3, self.width_label, self.width_input)
        self.layout.insertRow(4, self.length_label, self.length_input)

    def _check_add_brand(self, idx):
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

class RemoveImplantDialog(QDialog):
    def __init__(self, inventory, brand, type_, platform, width, length, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Remove Implants")
        self.setModal(True)
        self.setGeometry(300, 300, 700, 400)
        
        self.inventory = inventory

        # Get all matching implants from inventory
        self.matching_implants = [
            implant for implant in inventory
            if (implant["brand"] == brand and implant["type"] == type_ and
                implant["platform"] == platform and implant["width"] == width and
                implant["length"] == length)
        ]
        
        layout = QVBoxLayout(self)
        
        # Title label
        title_label = QLabel(f"Remove from {brand} - {type_} (Platform: {platform}, Size: {width}x{length})")
        layout.addWidget(title_label)
        
        # Table to display implants
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["REF", "LOT", "Expiry", "Qty in Stock", "Remove Qty"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Populate table with matching implants
        for implant in self.matching_implants:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(implant["ref"]))
            self.table.setItem(row, 1, QTableWidgetItem(implant["lot"]))
            self.table.setItem(row, 2, QTableWidgetItem(implant["expiry"]))
            self.table.setItem(row, 3, QTableWidgetItem(str(implant["qty"])))
            
            # Add spinbox for remove quantity
            spinbox = QSpinBox()
            spinbox.setMinimum(0)
            spinbox.setMaximum(implant["qty"])
            spinbox.setValue(0)
            self.table.setCellWidget(row, 4, spinbox)
        
        layout.addWidget(self.table)
        
        # OK and Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.on_ok_clicked)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def on_ok_clicked(self):
        """Gather removal selections and show confirmation dialog"""
        removals = []
        
        for row, implant in enumerate(self.matching_implants):
            spinbox = self.table.cellWidget(row, 4)
            remove_qty = spinbox.value()
            
            if remove_qty > 0:
                removals.append({
                    "ref": implant["ref"],
                    "lot": implant["lot"],
                    "expiry": implant["expiry"],
                    "remove_qty": remove_qty,
                    "inventory_index": self.inventory.index(implant)
                })
        
        if not removals:
            QMessageBox.information(self, "No Selection", "Please select at least one implant to remove.")
            return
        
        # Show confirmation dialog
        self.show_confirmation(removals)
    
    def show_confirmation(self, removals):
        """Show confirmation dialog with removal details"""
        confirmation_text = "You have selected the following implants to remove:\n\n"
        
        for removal in removals:
            confirmation_text += (
                f"REF: {removal['ref']}, LOT: {removal['lot']}, "
                f"Expiry: {removal['expiry']}\n"
                f"  Remove Qty: {removal['remove_qty']}\n\n"
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
    
    def get_removals(self):
        """Return list of removal operations"""
        return getattr(self, 'removals', [])

class AddHealingAbutmentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Healing Abutment")
        self.setModal(True)
        self.layout = QFormLayout(self)

        self.brand_input = QComboBox()
        self._brand_list = ["Nobel", "Straumann"]
        self._refresh_brand_items()
        self.brand_input.setCurrentText("Nobel")
        self.brand_input.currentIndexChanged.connect(self._check_add_brand)

        self.layout.addRow("Brand", self.brand_input)
        self.type_input = QLineEdit()
        self.layout.addRow("Type", self.type_input)
        self.platform_input = QLineEdit()
        self.layout.addRow("Platform", self.platform_input)
        self.width_input = QLineEdit()
        self.layout.addRow("Width", self.width_input)
        self.height_input = QLineEdit()
        self.layout.addRow("Height", self.height_input)
        self.expiry_input = QLineEdit()
        self.layout.addRow("Expiry (YYYY-MM-DD)", self.expiry_input)
        self.qty_input = QLineEdit()
        self.layout.addRow("Qty", self.qty_input)
        self.ref_input = QLineEdit()
        self.layout.addRow("REF", self.ref_input)
        self.lot_input = QLineEdit()
        self.layout.addRow("LOT", self.lot_input)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def _refresh_brand_items(self):
        self.brand_input.clear()
        brands_sorted = sorted(self._brand_list)
        self.brand_input.addItems(brands_sorted + ["Add another brand..."])

    def _check_add_brand(self, idx):
        if self.brand_input.currentText() == "Add another brand...":
            text, ok = QInputDialog.getText(self, "Add Brand", "Enter new brand name:")
            if ok and text.strip():
                new_brand = text.strip()
                if new_brand not in self._brand_list:
                    self._brand_list.append(new_brand)
                    self._refresh_brand_items()
                brands_sorted = sorted(self._brand_list)
                self.brand_input.setCurrentText(new_brand)
            else:
                brands_sorted = sorted(self._brand_list)
                self.brand_input.setCurrentText(brands_sorted[0])

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

class AddBoneGraftDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Bone Graft")
        self.setModal(True)
        self.layout = QFormLayout(self)

        self.brand_input = QComboBox()
        self._brand_list = ["Nobel", "Straumann"]
        self._refresh_brand_items()
        self.brand_input.setCurrentText("Nobel")
        self.brand_input.currentIndexChanged.connect(self._check_add_brand)

        self.layout.addRow("Brand", self.brand_input)
        self.type_input = QLineEdit()
        self.layout.addRow("Type", self.type_input)
        self.particulate_input = QLineEdit()
        self.layout.addRow("Particulate", self.particulate_input)
        self.granule_size_input = QLineEdit()
        self.layout.addRow("Granule Size", self.granule_size_input)
        self.amount_input = QLineEdit()
        self.layout.addRow("Amount", self.amount_input)
        self.expiry_input = QLineEdit()
        self.layout.addRow("Expiry (YYYY-MM-DD)", self.expiry_input)
        self.qty_input = QLineEdit()
        self.layout.addRow("Qty", self.qty_input)
        self.ref_input = QLineEdit()
        self.layout.addRow("REF", self.ref_input)
        self.lot_input = QLineEdit()
        self.layout.addRow("LOT", self.lot_input)
        self.sn_input = QLineEdit()
        self.layout.addRow("SN", self.sn_input)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def _refresh_brand_items(self):
        self.brand_input.clear()
        brands_sorted = sorted(self._brand_list)
        self.brand_input.addItems(brands_sorted + ["Add another brand..."])

    def _check_add_brand(self, idx):
        if self.brand_input.currentText() == "Add another brand...":
            text, ok = QInputDialog.getText(self, "Add Brand", "Enter new brand name:")
            if ok and text.strip():
                new_brand = text.strip()
                if new_brand not in self._brand_list:
                    self._brand_list.append(new_brand)
                    self._refresh_brand_items()
                brands_sorted = sorted(self._brand_list)
                self.brand_input.setCurrentText(new_brand)
            else:
                brands_sorted = sorted(self._brand_list)
                self.brand_input.setCurrentText(brands_sorted[0])

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

class RemoveHealingAbutmentDialog(QDialog):
    def __init__(self, inventory, brand, type_, platform, width, height, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Remove Healing Abutments")
        self.setModal(True)
        self.setGeometry(300, 300, 700, 400)
        
        self.inventory = inventory

        # Get all matching items from inventory
        self.matching_items = [
            item for item in inventory
            if (item["brand"] == brand and item["type"] == type_ and
                item["platform"] == platform and item["width"] == width and
                item["height"] == height)
        ]
        
        layout = QVBoxLayout(self)
        
        # Title label
        title_label = QLabel(f"Remove from {brand} - {type_} (Platform: {platform}, Size: {width}x{height})")
        layout.addWidget(title_label)
        
        # Table to display items
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["REF", "LOT", "Expiry", "Qty in Stock", "Remove Qty"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Populate table with matching items
        for item in self.matching_items:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(item["ref"]))
            self.table.setItem(row, 1, QTableWidgetItem(item["lot"]))
            self.table.setItem(row, 2, QTableWidgetItem(item["expiry"]))
            self.table.setItem(row, 3, QTableWidgetItem(str(item["qty"])))
            
            # Add spinbox for remove quantity
            spinbox = QSpinBox()
            spinbox.setMinimum(0)
            spinbox.setMaximum(item["qty"])
            spinbox.setValue(0)
            self.table.setCellWidget(row, 4, spinbox)
        
        layout.addWidget(self.table)
        
        # OK and Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.on_ok_clicked)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def on_ok_clicked(self):
        """Gather removal selections and show confirmation dialog"""
        removals = []
        
        for row, item in enumerate(self.matching_items):
            spinbox = self.table.cellWidget(row, 4)
            remove_qty = spinbox.value()
            
            if remove_qty > 0:
                removals.append({
                    "ref": item["ref"],
                    "lot": item["lot"],
                    "expiry": item["expiry"],
                    "remove_qty": remove_qty,
                    "inventory_index": self.inventory.index(item)
                })
        
        if not removals:
            QMessageBox.information(self, "No Selection", "Please select at least one item to remove.")
            return
        
        # Show confirmation dialog
        self.show_confirmation(removals)
    
    def show_confirmation(self, removals):
        """Show confirmation dialog with removal details"""
        confirmation_text = "You have selected the following items to remove:\n\n"
        
        for removal in removals:
            confirmation_text += (
                f"REF: {removal['ref']}, LOT: {removal['lot']}, "
                f"Expiry: {removal['expiry']}\n"
                f"  Remove Qty: {removal['remove_qty']}\n\n"
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
    
    def get_removals(self):
        """Return list of removal operations"""
        return getattr(self, 'removals', [])

class RemoveBoneGraftDialog(QDialog):
    def __init__(self, inventory, brand, type_, particulate, granule_size, amount, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Remove Bone Grafts")
        self.setModal(True)
        self.setGeometry(300, 300, 700, 400)
        
        self.inventory = inventory

        # Get all matching items from inventory
        self.matching_items = [
            item for item in inventory
            if (item["brand"] == brand and item["type"] == type_ and
                item["particulate"] == particulate and item["granule_size"] == granule_size and
                item["amount"] == amount)
        ]
        
        layout = QVBoxLayout(self)
        
        # Title label
        title_label = QLabel(f"Remove from {brand} - {type_} (Particulate: {particulate}, Granule Size: {granule_size}, Amount: {amount})")
        layout.addWidget(title_label)
        
        # Table to display items
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["REF", "LOT", "SN", "Expiry", "Qty in Stock", "Remove Qty"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Populate table with matching items
        for item in self.matching_items:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(item["ref"]))
            self.table.setItem(row, 1, QTableWidgetItem(item["lot"]))
            self.table.setItem(row, 2, QTableWidgetItem(item["sn"]))
            self.table.setItem(row, 3, QTableWidgetItem(item["expiry"]))
            self.table.setItem(row, 4, QTableWidgetItem(str(item["qty"])))
            
            # Add spinbox for remove quantity
            spinbox = QSpinBox()
            spinbox.setMinimum(0)
            spinbox.setMaximum(item["qty"])
            spinbox.setValue(0)
            self.table.setCellWidget(row, 5, spinbox)
        
        layout.addWidget(self.table)
        
        # OK and Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.on_ok_clicked)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def on_ok_clicked(self):
        """Gather removal selections and show confirmation dialog"""
        removals = []
        
        for row, item in enumerate(self.matching_items):
            spinbox = self.table.cellWidget(row, 5)
            remove_qty = spinbox.value()
            
            if remove_qty > 0:
                removals.append({
                    "ref": item["ref"],
                    "lot": item["lot"],
                    "sn": item["sn"],
                    "expiry": item["expiry"],
                    "remove_qty": remove_qty,
                    "inventory_index": self.inventory.index(item)
                })
        
        if not removals:
            QMessageBox.information(self, "No Selection", "Please select at least one item to remove.")
            return
        
        # Show confirmation dialog
        self.show_confirmation(removals)
    
    def show_confirmation(self, removals):
        """Show confirmation dialog with removal details"""
        confirmation_text = "You have selected the following items to remove:\n\n"
        
        for removal in removals:
            confirmation_text += (
                f"REF: {removal['ref']}, LOT: {removal['lot']}, SN: {removal['sn']}, "
                f"Expiry: {removal['expiry']}\n"
                f"  Remove Qty: {removal['remove_qty']}\n\n"
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
    
    def get_removals(self):
        """Return list of removal operations"""
        return getattr(self, 'removals', [])

class ImplantInventory(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dental Implant Inventory Manager")
        self.setGeometry(200, 200, 1200, 600)

        # Separate inventories for each product type
        self.implants_inventory = []
        self.abutments_inventory = []
        self.bone_grafts_inventory = []
        
        self.load_data()
        
        # Track selected row for each tab
        self.implants_selected_row = None
        self.abutments_selected_row = None
        self.bone_grafts_selected_row = None

        layout = QVBoxLayout()

        # Create tab widget
        tabs = QTabWidget()

        # ==================== IMPLANTS TAB ====================
        self.implants_widget = QWidget()
        implants_layout = QVBoxLayout()
        
        implants_btn_layout = QHBoxLayout()
        self.add_implant_btn = QPushButton("Add Implant")
        self.add_implant_btn.clicked.connect(self.add_implant)
        self.remove_implant_btn = QPushButton("Remove Implant")
        self.remove_implant_btn.clicked.connect(self.remove_implant)
        self.remove_implant_btn.setEnabled(False)
        self.save_implants_btn = QPushButton("Save All")
        self.save_implants_btn.clicked.connect(self.save_all_data)
        implants_btn_layout.addWidget(self.add_implant_btn)
        implants_btn_layout.addWidget(self.remove_implant_btn)
        implants_btn_layout.addWidget(self.save_implants_btn)
        implants_layout.addLayout(implants_btn_layout)
        
        self.implants_table = QTableWidget()
        self.implants_table.setColumnCount(9)
        self.implants_table.setHorizontalHeaderLabels([
            "Brand", "Type", "Platform", "Width", "Length", "Total Qty", "Most Recent Expiry", "Most Recent Expiry Qty", "Status"
        ])
        self.implants_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.implants_table.itemSelectionChanged.connect(self.on_implants_selection_changed)
        implants_layout.addWidget(self.implants_table)
        self.implants_widget.setLayout(implants_layout)
        tabs.addTab(self.implants_widget, "Implants")

        # ==================== HEALING ABUTMENTS TAB ====================
        self.abutments_widget = QWidget()
        abutments_layout = QVBoxLayout()
        
        abutments_btn_layout = QHBoxLayout()
        self.add_abutment_btn = QPushButton("Add Healing Abutment")
        self.add_abutment_btn.clicked.connect(self.add_abutment)
        self.remove_abutment_btn = QPushButton("Remove Healing Abutment")
        self.remove_abutment_btn.clicked.connect(self.remove_abutment)
        self.remove_abutment_btn.setEnabled(False)
        self.save_abutments_btn = QPushButton("Save All")
        self.save_abutments_btn.clicked.connect(self.save_all_data)
        abutments_btn_layout.addWidget(self.add_abutment_btn)
        abutments_btn_layout.addWidget(self.remove_abutment_btn)
        abutments_btn_layout.addWidget(self.save_abutments_btn)
        abutments_layout.addLayout(abutments_btn_layout)
        
        self.abutments_table = QTableWidget()
        self.abutments_table.setColumnCount(9)
        self.abutments_table.setHorizontalHeaderLabels([
            "Brand", "Type", "Platform", "Width", "Height", "Total Qty", "Most Recent Expiry", "Most Recent Expiry Qty", "Status"
        ])
        self.abutments_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.abutments_table.itemSelectionChanged.connect(self.on_abutments_selection_changed)
        abutments_layout.addWidget(self.abutments_table)
        self.abutments_widget.setLayout(abutments_layout)
        tabs.addTab(self.abutments_widget, "Healing Abutments")

        # ==================== BONE GRAFTS TAB ====================
        self.bone_grafts_widget = QWidget()
        bone_grafts_layout = QVBoxLayout()
        
        bone_grafts_btn_layout = QHBoxLayout()
        self.add_bone_graft_btn = QPushButton("Add Bone Graft")
        self.add_bone_graft_btn.clicked.connect(self.add_bone_graft)
        self.remove_bone_graft_btn = QPushButton("Remove Bone Graft")
        self.remove_bone_graft_btn.clicked.connect(self.remove_bone_graft)
        self.remove_bone_graft_btn.setEnabled(False)
        self.save_bone_grafts_btn = QPushButton("Save All")
        self.save_bone_grafts_btn.clicked.connect(self.save_all_data)
        bone_grafts_btn_layout.addWidget(self.add_bone_graft_btn)
        bone_grafts_btn_layout.addWidget(self.remove_bone_graft_btn)
        bone_grafts_btn_layout.addWidget(self.save_bone_grafts_btn)
        bone_grafts_layout.addLayout(bone_grafts_btn_layout)
        
        self.bone_grafts_table = QTableWidget()
        self.bone_grafts_table.setColumnCount(10)
        self.bone_grafts_table.setHorizontalHeaderLabels([
            "Brand", "Type", "Particulate", "Granule Size", "Amount", "Total Qty", "Most Recent Expiry", "Most Recent Expiry Qty", "Status", "SN"
        ])
        self.bone_grafts_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.bone_grafts_table.itemSelectionChanged.connect(self.on_bone_grafts_selection_changed)
        bone_grafts_layout.addWidget(self.bone_grafts_table)
        self.bone_grafts_widget.setLayout(bone_grafts_layout)
        tabs.addTab(self.bone_grafts_widget, "Bone Grafts")

        layout.addWidget(tabs)
        self.setLayout(layout)
        
        # Update all tables
        self.update_implants_table()
        self.update_abutments_table()
        self.update_bone_grafts_table()

    # ==================== IMPLANTS METHODS ====================
    def add_implant(self):
        dialog = AddImplantDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            brand = data["brand"]
            type_ = data["type"]
            platform = data["platform"]
            width = data["width"]
            length = data["length"]
            expiry = data["expiry"]
            qty_text = data["qty"]
            ref = data["ref"]
            lot = data["lot"]

            if not (brand and type_ and platform and width and length and expiry and qty_text and ref and lot):
                QMessageBox.warning(self, "Error", "All fields are required.")
                return

            try:
                expiry_date = datetime.strptime(expiry, "%Y-%m-%d")
            except ValueError:
                QMessageBox.warning(self, "Error", "Expiry must be YYYY-MM-DD")
                return

            try:
                qty = int(qty_text)
            except ValueError:
                QMessageBox.warning(self, "Error", "Quantity must be a number")
                return

            implant = {
                "brand": brand,
                "type": type_,
                "platform": platform,
                "width": width,
                "length": length,
                "expiry": expiry_date.strftime("%Y-%m-%d"),
                "qty": qty,
                "ref": ref,
                "lot": lot,
                "product_type": "implant"
            }
            self.implants_inventory.append(implant)
            self.update_implants_table()

    def on_implants_selection_changed(self):
        """Enable/disable remove button based on table selection"""
        selected_items = self.implants_table.selectedItems()
        if selected_items:
            self.implants_selected_row = selected_items[0].row()
            self.remove_implant_btn.setEnabled(True)
        else:
            self.implants_selected_row = None
            self.remove_implant_btn.setEnabled(False)

    def remove_implant(self):
        """Open dialog to remove selected implant"""
        if self.implants_selected_row is None:
            QMessageBox.warning(self, "Error", "Please select a row first.")
            return
        
        condensed_inventory = self._get_condensed_implants_inventory()
        selected_implant = condensed_inventory[self.implants_selected_row]
        
        dialog = RemoveImplantDialog(
            self.implants_inventory,
            selected_implant["brand"],
            selected_implant["type"],
            selected_implant["platform"],
            selected_implant["width"],
            selected_implant["length"],
            self
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            removals = dialog.get_removals()
            
            for removal in removals:
                inventory_index = removal["inventory_index"]
                remove_qty = removal["remove_qty"]
                
                if self.implants_inventory[inventory_index]["qty"] > remove_qty:
                    self.implants_inventory[inventory_index]["qty"] -= remove_qty
                else:
                    del self.implants_inventory[inventory_index]
            
            self.update_implants_table()
            QMessageBox.information(self, "Success", "Implants removed successfully.")

    def _get_condensed_implants_inventory(self):
        """Groups implants by brand, type, platform, width, and length."""
        grouped = {}
        
        for implant in self.implants_inventory:
            key = (implant["brand"], implant["type"], implant["platform"], implant["width"], implant["length"])
            
            if key not in grouped:
                grouped[key] = {
                    "brand": implant["brand"],
                    "type": implant["type"],
                    "platform": implant["platform"],
                    "width": implant["width"],
                    "length": implant["length"],
                    "total_qty": 0,
                    "expiries": []
                }
            
            grouped[key]["total_qty"] += implant["qty"]
            grouped[key]["expiries"].append({"date": implant["expiry"], "qty": implant["qty"]})
        
        condensed = []
        for implant_group in grouped.values():
            expiries_sorted = sorted(implant_group["expiries"], key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"), reverse=True)
            most_recent_expiry = expiries_sorted[0]["date"]
            most_recent_count = sum(e["qty"] for e in expiries_sorted if e["date"] == most_recent_expiry)
            
            condensed_item = {
                "brand": implant_group["brand"],
                "type": implant_group["type"],
                "platform": implant_group["platform"],
                "width": implant_group["width"],
                "length": implant_group["length"],
                "total_qty": implant_group["total_qty"],
                "most_recent_expiry": most_recent_expiry,
                "most_recent_expiry_qty": most_recent_count
            }
            condensed.append(condensed_item)
        
        return condensed

    def update_implants_table(self):
        self.implants_table.setRowCount(0)
        now = datetime.now()
        condensed_inventory = self._get_condensed_implants_inventory()

        for implant in sorted(condensed_inventory, key=lambda x: (x["brand"], x["type"], x["platform"], x["width"], x["length"], x["most_recent_expiry"])):
            row = self.implants_table.rowCount()
            self.implants_table.insertRow(row)
            self.implants_table.setItem(row, 0, QTableWidgetItem(implant["brand"]))
            self.implants_table.setItem(row, 1, QTableWidgetItem(implant["type"]))
            self.implants_table.setItem(row, 2, QTableWidgetItem(implant["platform"]))
            self.implants_table.setItem(row, 3, QTableWidgetItem(implant["width"]))
            self.implants_table.setItem(row, 4, QTableWidgetItem(implant["length"]))
            self.implants_table.setItem(row, 5, QTableWidgetItem(str(implant["total_qty"])))
            self.implants_table.setItem(row, 6, QTableWidgetItem(implant["most_recent_expiry"]))
            self.implants_table.setItem(row, 7, QTableWidgetItem(str(implant["most_recent_expiry_qty"])))

            try:
                expiry_date = datetime.strptime(implant["most_recent_expiry"], "%Y-%m-%d")
            except Exception:
                expiry_date = None
            status = ""
            if implant["total_qty"] <= 2:
                status = "⚠ Low Stock"
            if expiry_date and (expiry_date - now).days < 180:
                if status:
                    status += ", Expiring Soon"
                else:
                    status = "⚠ Expiring Soon"
            self.implants_table.setItem(row, 8, QTableWidgetItem(status))

    # ==================== HEALING ABUTMENTS METHODS ====================
    def add_abutment(self):
        dialog = AddHealingAbutmentDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            brand = data["brand"]
            type_ = data["type"]
            platform = data["platform"]
            width = data["width"]
            height = data["height"]
            expiry = data["expiry"]
            qty_text = data["qty"]
            ref = data["ref"]
            lot = data["lot"]

            if not (brand and type_ and platform and width and height and expiry and qty_text and ref and lot):
                QMessageBox.warning(self, "Error", "All fields are required.")
                return

            try:
                expiry_date = datetime.strptime(expiry, "%Y-%m-%d")
            except ValueError:
                QMessageBox.warning(self, "Error", "Expiry must be YYYY-MM-DD")
                return

            try:
                qty = int(qty_text)
            except ValueError:
                QMessageBox.warning(self, "Error", "Quantity must be a number")
                return

            abutment = {
                "brand": brand,
                "type": type_,
                "platform": platform,
                "width": width,
                "height": height,
                "expiry": expiry_date.strftime("%Y-%m-%d"),
                "qty": qty,
                "ref": ref,
                "lot": lot,
                "product_type": "abutment"
            }
            self.abutments_inventory.append(abutment)
            self.update_abutments_table()

    def on_abutments_selection_changed(self):
        """Enable/disable remove button based on table selection"""
        selected_items = self.abutments_table.selectedItems()
        if selected_items:
            self.abutments_selected_row = selected_items[0].row()
            self.remove_abutment_btn.setEnabled(True)
        else:
            self.abutments_selected_row = None
            self.remove_abutment_btn.setEnabled(False)

    def remove_abutment(self):
        """Open dialog to remove selected abutment"""
        if self.abutments_selected_row is None:
            QMessageBox.warning(self, "Error", "Please select a row first.")
            return
        
        condensed_inventory = self._get_condensed_abutments_inventory()
        selected_abutment = condensed_inventory[self.abutments_selected_row]
        
        dialog = RemoveHealingAbutmentDialog(
            self.abutments_inventory,
            selected_abutment["brand"],
            selected_abutment["type"],
            selected_abutment["platform"],
            selected_abutment["width"],
            selected_abutment["height"],
            self
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            removals = dialog.get_removals()
            
            for removal in removals:
                inventory_index = removal["inventory_index"]
                remove_qty = removal["remove_qty"]
                
                if self.abutments_inventory[inventory_index]["qty"] > remove_qty:
                    self.abutments_inventory[inventory_index]["qty"] -= remove_qty
                else:
                    del self.abutments_inventory[inventory_index]
            
            self.update_abutments_table()
            QMessageBox.information(self, "Success", "Healing abutments removed successfully.")

    def _get_condensed_abutments_inventory(self):
        """Groups abutments by brand, type, platform, width, and height."""
        grouped = {}
        
        for abutment in self.abutments_inventory:
            key = (abutment["brand"], abutment["type"], abutment["platform"], abutment["width"], abutment["height"])
            
            if key not in grouped:
                grouped[key] = {
                    "brand": abutment["brand"],
                    "type": abutment["type"],
                    "platform": abutment["platform"],
                    "width": abutment["width"],
                    "height": abutment["height"],
                    "total_qty": 0,
                    "expiries": []
                }
            
            grouped[key]["total_qty"] += abutment["qty"]
            grouped[key]["expiries"].append({"date": abutment["expiry"], "qty": abutment["qty"]})
        
        condensed = []
        for abutment_group in grouped.values():
            expiries_sorted = sorted(abutment_group["expiries"], key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"), reverse=True)
            most_recent_expiry = expiries_sorted[0]["date"]
            most_recent_count = sum(e["qty"] for e in expiries_sorted if e["date"] == most_recent_expiry)
            
            condensed_item = {
                "brand": abutment_group["brand"],
                "type": abutment_group["type"],
                "platform": abutment_group["platform"],
                "width": abutment_group["width"],
                "height": abutment_group["height"],
                "total_qty": abutment_group["total_qty"],
                "most_recent_expiry": most_recent_expiry,
                "most_recent_expiry_qty": most_recent_count
            }
            condensed.append(condensed_item)
        
        return condensed

    def update_abutments_table(self):
        self.abutments_table.setRowCount(0)
        now = datetime.now()
        condensed_inventory = self._get_condensed_abutments_inventory()

        for abutment in sorted(condensed_inventory, key=lambda x: (x["brand"], x["type"], x["platform"], x["width"], x["height"], x["most_recent_expiry"])):
            row = self.abutments_table.rowCount()
            self.abutments_table.insertRow(row)
            self.abutments_table.setItem(row, 0, QTableWidgetItem(abutment["brand"]))
            self.abutments_table.setItem(row, 1, QTableWidgetItem(abutment["type"]))
            self.abutments_table.setItem(row, 2, QTableWidgetItem(abutment["platform"]))
            self.abutments_table.setItem(row, 3, QTableWidgetItem(abutment["width"]))
            self.abutments_table.setItem(row, 4, QTableWidgetItem(abutment["height"]))
            self.abutments_table.setItem(row, 5, QTableWidgetItem(str(abutment["total_qty"])))
            self.abutments_table.setItem(row, 6, QTableWidgetItem(abutment["most_recent_expiry"]))
            self.abutments_table.setItem(row, 7, QTableWidgetItem(str(abutment["most_recent_expiry_qty"])))

            try:
                expiry_date = datetime.strptime(abutment["most_recent_expiry"], "%Y-%m-%d")
            except Exception:
                expiry_date = None
            status = ""
            if abutment["total_qty"] <= 2:
                status = "⚠ Low Stock"
            if expiry_date and (expiry_date - now).days < 180:
                if status:
                    status += ", Expiring Soon"
                else:
                    status = "⚠ Expiring Soon"
            self.abutments_table.setItem(row, 8, QTableWidgetItem(status))

    # ==================== BONE GRAFTS METHODS ====================
    def add_bone_graft(self):
        dialog = AddBoneGraftDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            brand = data["brand"]
            type_ = data["type"]
            particulate = data["particulate"]
            granule_size = data["granule_size"]
            amount = data["amount"]
            expiry = data["expiry"]
            qty_text = data["qty"]
            ref = data["ref"]
            lot = data["lot"]
            sn = data["sn"]

            if not (brand and type_ and particulate and granule_size and amount and expiry and qty_text and ref and lot and sn):
                QMessageBox.warning(self, "Error", "All fields are required.")
                return

            try:
                expiry_date = datetime.strptime(expiry, "%Y-%m-%d")
            except ValueError:
                QMessageBox.warning(self, "Error", "Expiry must be YYYY-MM-DD")
                return

            try:
                qty = int(qty_text)
            except ValueError:
                QMessageBox.warning(self, "Error", "Quantity must be a number")
                return

            bone_graft = {
                "brand": brand,
                "type": type_,
                "particulate": particulate,
                "granule_size": granule_size,
                "amount": amount,
                "expiry": expiry_date.strftime("%Y-%m-%d"),
                "qty": qty,
                "ref": ref,
                "lot": lot,
                "sn": sn,
                "product_type": "bone_graft"
            }
            self.bone_grafts_inventory.append(bone_graft)
            self.update_bone_grafts_table()

    def on_bone_grafts_selection_changed(self):
        """Enable/disable remove button based on table selection"""
        selected_items = self.bone_grafts_table.selectedItems()
        if selected_items:
            self.bone_grafts_selected_row = selected_items[0].row()
            self.remove_bone_graft_btn.setEnabled(True)
        else:
            self.bone_grafts_selected_row = None
            self.remove_bone_graft_btn.setEnabled(False)

    def remove_bone_graft(self):
        """Open dialog to remove selected bone graft"""
        if self.bone_grafts_selected_row is None:
            QMessageBox.warning(self, "Error", "Please select a row first.")
            return
        
        condensed_inventory = self._get_condensed_bone_grafts_inventory()
        selected_bone_graft = condensed_inventory[self.bone_grafts_selected_row]
        
        dialog = RemoveBoneGraftDialog(
            self.bone_grafts_inventory,
            selected_bone_graft["brand"],
            selected_bone_graft["type"],
            selected_bone_graft["particulate"],
            selected_bone_graft["granule_size"],
            selected_bone_graft["amount"],
            self
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            removals = dialog.get_removals()
            
            for removal in removals:
                inventory_index = removal["inventory_index"]
                remove_qty = removal["remove_qty"]
                
                if self.bone_grafts_inventory[inventory_index]["qty"] > remove_qty:
                    self.bone_grafts_inventory[inventory_index]["qty"] -= remove_qty
                else:
                    del self.bone_grafts_inventory[inventory_index]
            
            self.update_bone_grafts_table()
            QMessageBox.information(self, "Success", "Bone grafts removed successfully.")

    def _get_condensed_bone_grafts_inventory(self):
        """Groups bone grafts by brand, type, particulate, granule size, and amount."""
        grouped = {}
        
        for bone_graft in self.bone_grafts_inventory:
            key = (bone_graft["brand"], bone_graft["type"], bone_graft["particulate"], bone_graft["granule_size"], bone_graft["amount"])
            
            if key not in grouped:
                grouped[key] = {
                    "brand": bone_graft["brand"],
                    "type": bone_graft["type"],
                    "particulate": bone_graft["particulate"],
                    "granule_size": bone_graft["granule_size"],
                    "amount": bone_graft["amount"],
                    "total_qty": 0,
                    "expiries": []
                }
            
            grouped[key]["total_qty"] += bone_graft["qty"]
            grouped[key]["expiries"].append({"date": bone_graft["expiry"], "qty": bone_graft["qty"]})
        
        condensed = []
        for bone_graft_group in grouped.values():
            expiries_sorted = sorted(bone_graft_group["expiries"], key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"), reverse=True)
            most_recent_expiry = expiries_sorted[0]["date"]
            most_recent_count = sum(e["qty"] for e in expiries_sorted if e["date"] == most_recent_expiry)
            
            condensed_item = {
                "brand": bone_graft_group["brand"],
                "type": bone_graft_group["type"],
                "particulate": bone_graft_group["particulate"],
                "granule_size": bone_graft_group["granule_size"],
                "amount": bone_graft_group["amount"],
                "total_qty": bone_graft_group["total_qty"],
                "most_recent_expiry": most_recent_expiry,
                "most_recent_expiry_qty": most_recent_count
            }
            condensed.append(condensed_item)
        
        return condensed

    def update_bone_grafts_table(self):
        self.bone_grafts_table.setRowCount(0)
        now = datetime.now()
        condensed_inventory = self._get_condensed_bone_grafts_inventory()

        for bone_graft in sorted(condensed_inventory, key=lambda x: (x["brand"], x["type"], x["particulate"], x["granule_size"], x["amount"], x["most_recent_expiry"])):
            row = self.bone_grafts_table.rowCount()
            self.bone_grafts_table.insertRow(row)
            self.bone_grafts_table.setItem(row, 0, QTableWidgetItem(bone_graft["brand"]))
            self.bone_grafts_table.setItem(row, 1, QTableWidgetItem(bone_graft["type"]))
            self.bone_grafts_table.setItem(row, 2, QTableWidgetItem(bone_graft["particulate"]))
            self.bone_grafts_table.setItem(row, 3, QTableWidgetItem(bone_graft["granule_size"]))
            self.bone_grafts_table.setItem(row, 4, QTableWidgetItem(bone_graft["amount"]))
            self.bone_grafts_table.setItem(row, 5, QTableWidgetItem(str(bone_graft["total_qty"])))
            self.bone_grafts_table.setItem(row, 6, QTableWidgetItem(bone_graft["most_recent_expiry"]))
            self.bone_grafts_table.setItem(row, 7, QTableWidgetItem(str(bone_graft["most_recent_expiry_qty"])))

            try:
                expiry_date = datetime.strptime(bone_graft["most_recent_expiry"], "%Y-%m-%d")
            except Exception:
                expiry_date = None
            status = ""
            if bone_graft["total_qty"] <= 2:
                status = "⚠ Low Stock"
            if expiry_date and (expiry_date - now).days < 180:
                if status:
                    status += ", Expiring Soon"
                else:
                    status = "⚠ Expiring Soon"
            self.bone_grafts_table.setItem(row, 8, QTableWidgetItem(status))
            # SN column
            # Note: We'll add SN later if needed

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Save Inventory",
            "Do you want to save the inventory to file before exiting?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
        )
        if reply == QMessageBox.StandardButton.Yes:
            # Save each product file separately
            self.save_implants_data()
            self.save_abutments_data()
            self.save_bone_grafts_data()
            event.accept()
        elif reply == QMessageBox.StandardButton.No:
            event.accept()
        else:
            event.ignore()
    def save_implants_data(self):
        try:
            with open(IMPLANTS_FILE, "w", newline="") as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(["Brand", "Type", "Platform", "Width", "Length", "Expiry", "Qty", "REF", "LOT"])
                for implant in self.implants_inventory:
                    writer.writerow([
                        implant["brand"],
                        implant["type"],
                        implant["platform"],
                        implant["width"],
                        implant["length"],
                        implant["expiry"],
                        implant["qty"],
                        implant["ref"],
                        implant["lot"]
                    ])
            QMessageBox.information(self, "Saved", f"Implants saved to {IMPLANTS_FILE}.")
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Failed to save implants: {e}")

    def save_abutments_data(self):
        try:
            with open(ABUTMENTS_FILE, "w", newline="") as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(["Brand", "Type", "Platform", "Width", "Height", "Expiry", "Qty", "REF", "LOT"])
                for abutment in self.abutments_inventory:
                    writer.writerow([
                        abutment["brand"],
                        abutment["type"],
                        abutment["platform"],
                        abutment["width"],
                        abutment["height"],
                        abutment["expiry"],
                        abutment["qty"],
                        abutment["ref"],
                        abutment["lot"]
                    ])
            QMessageBox.information(self, "Saved", f"Healing abutments saved to {ABUTMENTS_FILE}.")
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Failed to save abutments: {e}")

    def save_bone_grafts_data(self):
        try:
            with open(BONE_GRAFTS_FILE, "w", newline="") as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(["Brand", "Type", "Particulate", "Granule Size", "Amount", "Expiry", "Qty", "REF", "LOT", "SN"])
                for graft in self.bone_grafts_inventory:
                    writer.writerow([
                        graft["brand"],
                        graft["type"],
                        graft["particulate"],
                        graft["granule_size"],
                        graft["amount"],
                        graft["expiry"],
                        graft["qty"],
                        graft["ref"],
                        graft["lot"],
                        graft["sn"]
                    ])
            QMessageBox.information(self, "Saved", f"Bone grafts saved to {BONE_GRAFTS_FILE}.")
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Failed to save bone grafts: {e}")

    def save_all_data(self):
        """Save all three product files."""
        self.save_implants_data()
        self.save_abutments_data()
        self.save_bone_grafts_data()
        QMessageBox.information(self, "Saved", "All inventories saved successfully.")

    def load_data(self):
        # Load implants
        try:
            with open(IMPLANTS_FILE, "r") as f:
                reader = csv.reader(f)
                for row in reader:
                    # Skip header row if present
                    if not row:
                        continue
                    if row[0].strip().lower() == "brand" or (len(row) > 5 and row[5].strip().lower() == "expiry"):
                        continue
                    if len(row) != 9:
                        continue
                    self.implants_inventory.append({
                        "brand": row[0],
                        "type": row[1],
                        "platform": row[2],
                        "width": row[3],
                        "length": row[4],
                        "expiry": row[5],
                        "qty": int(row[6]),
                        "ref": row[7],
                        "lot": row[8]
                    })
        except FileNotFoundError:
            pass

        # Load abutments
        try:
            with open(ABUTMENTS_FILE, "r") as f:
                reader = csv.reader(f)
                for row in reader:
                    # Skip header row if present
                    if not row:
                        continue
                    if row[0].strip().lower() == "brand" or (len(row) > 5 and row[5].strip().lower() == "expiry"):
                        continue
                    if len(row) != 9:
                        continue
                    self.abutments_inventory.append({
                        "brand": row[0],
                        "type": row[1],
                        "platform": row[2],
                        "width": row[3],
                        "height": row[4],
                        "expiry": row[5],
                        "qty": int(row[6]),
                        "ref": row[7],
                        "lot": row[8]
                    })
        except FileNotFoundError:
            pass

        # Load bone grafts
        try:
            with open(BONE_GRAFTS_FILE, "r") as f:
                reader = csv.reader(f)
                for row in reader:
                    # Skip header row if present
                    if not row:
                        continue
                    if row[0].strip().lower() == "brand" or (len(row) > 5 and row[5].strip().lower() == "expiry"):
                        continue
                    if len(row) != 10:
                        continue
                    self.bone_grafts_inventory.append({
                        "brand": row[0],
                        "type": row[1],
                        "particulate": row[2],
                        "granule_size": row[3],
                        "amount": row[4],
                        "expiry": row[5],
                        "qty": int(row[6]),
                        "ref": row[7],
                        "lot": row[8],
                        "sn": row[9]
                    })
        except FileNotFoundError:
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImplantInventory()
    window.show()
    sys.exit(app.exec())
