import sys
import os
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox, QListWidgetItem

try:
    # Case 1: Running this file directly (python app_contacts/main.py)
    from parser import ContactParser
    from ui_layout import ContactViewerUI
except ImportError:
    # Case 2: Running from root dashboard (python main.py)
    # USE DOTS HERE to point to the folder structure
    from app_contacts.parser import ContactParser
    from app_contacts.ui_layout import ContactViewerUI



class ContactApp(ContactViewerUI):
    def __init__(self):
        super().__init__()
        self.contacts_data = []  # Store full data

        # Connect Signals
        self.contact_list.itemClicked.connect(self.on_contact_selected)

        # Auto-load file on startup
        self.load_file_dialog()

    def load_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Google Contacts VCF",
            "",
            "VCF Files (*.vcf);;All Files (*)"
        )

        if file_path:
            self.load_contacts(file_path)
        else:
            # If user cancels, maybe show a blank screen or close?
            # For now, we just stay open.
            pass

    def load_contacts(self, path):
        self.contacts_data = ContactParser.parse_vcf(path)

        if not self.contacts_data:
            QMessageBox.warning(self, "Error", "No contacts found or failed to parse.")
            return

        self.contact_list.clear()
        for contact in self.contacts_data:
            item = QListWidgetItem(contact['name'])
            # Store the actual data index in the item so we can retrieve it easily
            item.setData(100, contact)
            self.contact_list.addItem(item)

        self.search_label.setText(f"Contacts ({len(self.contacts_data)})")

    def on_contact_selected(self, item):
        # Retrieve the data dictionary we stored in the item
        data = item.data(100)
        self.update_details(data)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Optional: Set a global font for the app
    font = app.font()
    font.setPointSize(10)
    app.setFont(font)

    window = ContactApp()
    window.show()
    sys.exit(app.exec())
