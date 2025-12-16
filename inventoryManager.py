import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QMessageBox, QTabWidget
)
from implants import ImplantInventory
from healingAbutments import HealingAbutmentInventory
from boneGrafts import BoneGraftInventory

IMPLANTS_FILE = "Inventory/implants.csv"
HEALING_ABUTMENTS_FILE = "Inventory/healing_abutments.csv"
BONE_GRAFTS_FILE = "Inventory/bone_grafts.csv"
IMPLANTS_LOW_QUANTITY = 1
HEALING_ABUTMENTS_LOW_QUANTITY = 2
BONE_GRAFTS_LOW_QUANTITY = 2
DAYS_FROM_EXPIRY = 180

class InventoryManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Manager")
        self.setGeometry(200, 200, 1600, 800)

        self.implant_inventory = ImplantInventory(
            inventory_file=IMPLANTS_FILE,
            low_quantity=IMPLANTS_LOW_QUANTITY,
            days_from_expiry=DAYS_FROM_EXPIRY
        )
        self.healing_abutment_inventory = HealingAbutmentInventory(
            inventory_file=HEALING_ABUTMENTS_FILE,
            low_quantity=HEALING_ABUTMENTS_LOW_QUANTITY,
            days_from_expiry=DAYS_FROM_EXPIRY
        )
        self.bone_graft_inventory = BoneGraftInventory(
            inventory_file=BONE_GRAFTS_FILE,
            low_quantity=BONE_GRAFTS_LOW_QUANTITY,
            days_from_expiry=DAYS_FROM_EXPIRY
        )

        # Load data from files       
        self.load_data()
        
        layout = QVBoxLayout()
        tabs = QTabWidget()
        tabs.addTab(self.implant_inventory.widget, "Implants")
        tabs.addTab(self.healing_abutment_inventory.widget, "Healing Abutments")
        tabs.addTab(self.bone_graft_inventory.widget, "Bone Grafts")
        layout.addWidget(tabs)
        self.setLayout(layout)
        
        # Update all tables
        self.implant_inventory.update_table()
        self.healing_abutment_inventory.update_table()
        self.bone_graft_inventory.update_table()

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Save Inventory",
            "Do you want to save the inventory to file before exiting?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
        )
        if reply == QMessageBox.StandardButton.Yes:
            # Save each product file separately
            self.implant_inventory.save_data()
            self.healing_abutment_inventory.save_data()
            self.bone_graft_inventory.save_data()
            event.accept()
        elif reply == QMessageBox.StandardButton.No:
            event.accept()
        else:
            event.ignore()

    def save_all_data(self):
        """Save all three product files."""
        #self.save_implants_data()
        self.implant_inventory.save_data()
        self.healing_abutment_inventory.save_data()
        self.bone_graft_inventory.save_data()
        QMessageBox.information(self, "Saved", "All inventories saved successfully.")

    def load_data(self):
        # Load implants
        self.implant_inventory.load_data()
        self.healing_abutment_inventory.load_data()
        self.bone_graft_inventory.load_data()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InventoryManager()
    window.show()
    sys.exit(app.exec())
