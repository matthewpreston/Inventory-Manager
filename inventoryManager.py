import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QMessageBox, QTabWidget
)
from baseInventory import Inventory
from implants import ImplantInventory
from healingAbutments import HealingAbutmentInventory
from coverScrews import CoverScrewInventory
from temporaryAbutments import TemporaryAbutmentInventory
from boneGrafts import BoneGraftInventory
from membranes import MembraneInventory

THIS_FILE_PATH = os.path.dirname(os.path.abspath(__file__))

IMPLANTS_FILE = os.path.join(THIS_FILE_PATH, "Inventory", "implants.csv")
HEALING_ABUTMENTS_FILE = os.path.join(THIS_FILE_PATH, "Inventory", "healing_abutments.csv")
COVER_SCREWS_FILE = os.path.join(THIS_FILE_PATH, "Inventory", "cover_screws.csv")
TEMPORARY_ABUTMENTS_FILE = os.path.join(THIS_FILE_PATH, "Inventory", "temporary_abutments.csv")
BONE_GRAFTS_FILE = os.path.join(THIS_FILE_PATH, "Inventory", "bone_grafts.csv")
MEMBRANES_FILE = os.path.join(THIS_FILE_PATH, "Inventory", "membranes.csv")
IMPLANTS_LOW_QUANTITY = 1
HEALING_ABUTMENTS_LOW_QUANTITY = 2
COVER_SCREWS_LOW_QUANTITY = 2
TEMPORARY_ABUTMENTS_LOW_QUANTITY = 2
BONE_GRAFTS_LOW_QUANTITY = 2
MEMBRANES_LOW_QUANTITY = 2
DAYS_FROM_EXPIRY = 180
DAYS_FROM_EXPIRY_WARNING = 60

class InventoryManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Manager")
        self.setGeometry(200, 200, 1600, 800)

        self.inventories: dict[str, Inventory] = {
            "Implants": ImplantInventory(
                inventory_file=IMPLANTS_FILE,
                low_quantity=IMPLANTS_LOW_QUANTITY,
                days_from_expiry=DAYS_FROM_EXPIRY,
                days_from_expiry_warning=DAYS_FROM_EXPIRY_WARNING
            ),
            "Healing Abutments": HealingAbutmentInventory(
                inventory_file=HEALING_ABUTMENTS_FILE,
                low_quantity=HEALING_ABUTMENTS_LOW_QUANTITY,
                days_from_expiry=DAYS_FROM_EXPIRY,
                days_from_expiry_warning=DAYS_FROM_EXPIRY_WARNING
            ),
            "Cover Screws": CoverScrewInventory(
                inventory_file=COVER_SCREWS_FILE,
                low_quantity=COVER_SCREWS_LOW_QUANTITY,
                days_from_expiry=DAYS_FROM_EXPIRY,
                days_from_expiry_warning=DAYS_FROM_EXPIRY_WARNING
            ),
            "Temporary Abutments": TemporaryAbutmentInventory(
                inventory_file=TEMPORARY_ABUTMENTS_FILE,
                low_quantity=TEMPORARY_ABUTMENTS_LOW_QUANTITY,
                days_from_expiry=DAYS_FROM_EXPIRY,
                days_from_expiry_warning=DAYS_FROM_EXPIRY_WARNING
            ),
            "Bone Grafts": BoneGraftInventory(
                inventory_file=BONE_GRAFTS_FILE,
                low_quantity=BONE_GRAFTS_LOW_QUANTITY,
                days_from_expiry=DAYS_FROM_EXPIRY,
                days_from_expiry_warning=DAYS_FROM_EXPIRY_WARNING
            ),
            "Membranes": MembraneInventory(
                inventory_file=MEMBRANES_FILE,
                low_quantity=MEMBRANES_LOW_QUANTITY,
                days_from_expiry=DAYS_FROM_EXPIRY,
                days_from_expiry_warning=DAYS_FROM_EXPIRY_WARNING
            )
        }

        layout = QVBoxLayout()
        tabs = QTabWidget()
        for title, inventory in self.inventories.items():
            inventory.save_btn.clicked.disconnect()
            inventory.save_btn.clicked.connect(self.save_all_data)
            inventory.load_data()
            tabs.addTab(inventory.widget, title)
            inventory.update_table()
        layout.addWidget(tabs)
        self.setLayout(layout)

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Save Inventory",
            "Do you want to save the inventory to file before exiting?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.save_all_data()
            event.accept()
        elif reply == QMessageBox.StandardButton.No:
            event.accept()
        else:
            event.ignore()

    def save_all_data(self):
        """Save all three product files."""
        for inventory in self.inventories.values():
            inventory.save_data(showMessageBox=False)
        QMessageBox.information(self, "Saved", "All inventories saved successfully.")

    def load_data(self):
        for inventory in self.inventories.values():
            inventory.load_data()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InventoryManager()
    window.show()
    sys.exit(app.exec())
