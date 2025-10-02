import sys
import csv
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QDialog, QDialogButtonBox, QFormLayout, QComboBox, QInputDialog
)

DATA_FILE = "implants.csv"


# Dialog for implant input
class ImplantDialog(QDialog):
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
                "NobelParallel TiUnite",
                "NobelParallel TiUltra",
                "NobelActive TiUltra"
            ])
            # Platform
            self.platform_input = QComboBox()
            self.platform_input.addItems(["3.0", "RP", "NP", "WP"])
            # Width
            self.width_input = QComboBox()
            self.width_input.addItems(["3.0", "3.5", "4.3", "5.0", "5.5"])
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


class ImplantInventory(QWidget):
    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Save Inventory",
            "Do you want to save the inventory to file before exiting?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.save_data()
            event.accept()
        elif reply == QMessageBox.StandardButton.No:
            event.accept()
        else:
            event.ignore()
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dental Implant Inventory Manager")
        self.setGeometry(200, 200, 800, 400)

        self.inventory = []
        self.load_data()

        layout = QVBoxLayout()

        # Buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Implant")
        add_btn.clicked.connect(self.add_implant)
        save_btn = QPushButton("Save Inventory")
        save_btn.clicked.connect(self.save_data)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Brand", "Type", "Platform", "Width", "Length", "Expiry", "Qty", "REF", "LOT", "Status"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.update_table()
        self.update_table()


    def add_implant(self):
        dialog = ImplantDialog(self)
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
                "lot": lot
            }
            self.inventory.append(implant)
            self.update_table()

    def update_table(self):
        self.table.setRowCount(0)
        now = datetime.now()
        for implant in self.inventory:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(implant["brand"]))
            self.table.setItem(row, 1, QTableWidgetItem(implant["type"]))
            self.table.setItem(row, 2, QTableWidgetItem(implant["platform"]))
            self.table.setItem(row, 3, QTableWidgetItem(implant["width"]))
            self.table.setItem(row, 4, QTableWidgetItem(implant["length"]))
            self.table.setItem(row, 5, QTableWidgetItem(implant["expiry"]))
            self.table.setItem(row, 6, QTableWidgetItem(str(implant["qty"])))
            self.table.setItem(row, 7, QTableWidgetItem(implant["ref"]))
            self.table.setItem(row, 8, QTableWidgetItem(implant["lot"]))
            # Status column
            try:
                expiry_date = datetime.strptime(implant["expiry"], "%Y-%m-%d")
            except Exception:
                expiry_date = None
            status = ""
            if implant["qty"] <= 2:
                status = "⚠ Low Stock"
            elif expiry_date and (expiry_date - now).days < 180:
                status = "⚠ Expiring Soon"
            self.table.setItem(row, 9, QTableWidgetItem(status))

    def save_data(self):
        with open(DATA_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            for implant in self.inventory:
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
        QMessageBox.information(self, "Saved", "Inventory saved successfully.")

    def load_data(self):
        try:
            with open(DATA_FILE, "r") as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) == 9:
                        self.inventory.append({
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImplantInventory()
    window.show()
    sys.exit(app.exec())
