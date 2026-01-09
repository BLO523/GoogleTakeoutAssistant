import sys
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox, QHeaderView, QAbstractButton
from PyQt6.QtCore import QThread, pyqtSignal, Qt

# Adjust imports based on your folder structure
try:
    from parser import MboxParser
    from ui_layout import MailViewerUI
    from model import EmailTableModel
except ImportError:
    from app_mail.parser import MboxParser
    from app_mail.ui_layout import MailViewerUI
    from app_mail.model import EmailTableModel


class HeaderLoaderThread(QThread):
    batch_loaded = pyqtSignal(list)
    progress_updated = pyqtSignal(int)
    finished_loading = pyqtSignal(int)

    def __init__(self, parser, total_count):
        super().__init__()
        self.parser = parser
        self.total_count = total_count
        self.is_running = True

    def run(self):
        batch_size = 50
        current_batch = []
        count = 0

        for item in self.parser.get_headers_generator():
            if not self.is_running: break

            current_batch.append(item)
            count += 1

            if len(current_batch) >= batch_size:
                self.batch_loaded.emit(current_batch)
                current_batch = []

                if self.total_count > 0:
                    pct = int((count / self.total_count) * 100)
                    self.progress_updated.emit(pct)

        if current_batch:
            self.batch_loaded.emit(current_batch)

        self.finished_loading.emit(count)

    def stop(self):
        self.is_running = False


class MailApp(MailViewerUI):
    def __init__(self):
        super().__init__()
        self.parser = MboxParser()
        self.loader_thread = None
        self.loading_notification = None

        # References for our custom buttons
        self.btn_exit_app = None
        self.btn_background = None

        # Setup Model
        self.model = EmailTableModel()
        self.mail_table.setModel(self.model)

        # Table Column sizing
        header = self.mail_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.mail_table.setColumnWidth(0, 200)
        self.mail_table.setColumnWidth(2, 140)

        self.mail_table.clicked.connect(self.on_email_selected)
        self.search_input.textChanged.connect(self.on_search_changed)
        self.folder_list.itemClicked.connect(self.on_folder_changed)

        self.load_file_dialog()

    def load_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open MBOX", "", "MBOX (*.mbox);;All (*)")
        if file_path:
            self.start_loading(file_path)
        else:
            sys.exit()

    def start_loading(self, path):
        # Reset UI
        self.model.clear()
        self.folder_list.clear()
        self.web_view.setHtml("")
        self.search_input.clear()

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.lbl_status.setText("Preparing to scan file...")

        # --- SHOW LOADING POPUP ---
        self.loading_notification = QMessageBox(self)
        self.loading_notification.setWindowTitle("Please Wait")
        self.loading_notification.setText(f"Loading large mailbox file...\n\nThis process may take several minutes.")
        self.loading_notification.setWindowModality(Qt.WindowModality.ApplicationModal)

        # --- CUSTOM BUTTONS ---
        # 1. Exit App (Destructive role usually places it to the left or right depending on OS)
        self.btn_exit_app = self.loading_notification.addButton("Exit Application",
                                                                QMessageBox.ButtonRole.DestructiveRole)

        # 2. Run in Background (Action role)
        self.btn_background = self.loading_notification.addButton("Run in Background",
                                                                  QMessageBox.ButtonRole.ActionRole)

        # Connect signal
        self.loading_notification.buttonClicked.connect(self.on_popup_action)

        self.loading_notification.show()
        QApplication.processEvents()

        try:
            total = self.parser.load_mbox(path)
            self.lbl_status.setText(f"Scanning {total} emails...")

            self.loader_thread = HeaderLoaderThread(self.parser, total)
            self.loader_thread.batch_loaded.connect(self.on_batch_added)
            self.loader_thread.progress_updated.connect(self.on_progress)
            self.loader_thread.finished_loading.connect(self.on_loading_finished)
            self.loader_thread.start()

        except Exception as e:
            if self.loading_notification:
                self.loading_notification.close()
            QMessageBox.critical(self, "Error", str(e))
            self.progress_bar.setVisible(False)

    def on_popup_action(self, button: QAbstractButton):
        """Handle custom buttons on the loading popup"""

        # OPTION 1: Exit Application
        if button == self.btn_exit_app:
            self.lbl_status.setText("Stopping...")
            self.close()  # This triggers closeEvent, which stops the thread cleanly

        # OPTION 2: Run in Background
        elif button == self.btn_background:
            # We just close the popup.
            # The Window Modality is removed, so the user can click the table.
            # The thread continues running in the background.
            if self.loading_notification:
                self.loading_notification.close()
                self.loading_notification = None

            self.lbl_status.setText("Loading continuing in background...")

    def on_batch_added(self, batch):
        self.model.add_rows(batch)

    def on_progress(self, percent):
        self.progress_bar.setValue(percent)
        # Only update text if the window is actually open
        if self.loading_notification:
            self.loading_notification.setText(f"Loading large mailbox file...\n\nProgress: {percent}%")

    def on_loading_finished(self, total_loaded):
        self.progress_bar.setVisible(False)
        self.lbl_status.setText(f"Done. {total_loaded} emails loaded.")

        # Close popup if it's still open
        if self.loading_notification:
            self.loading_notification.close()
            self.loading_notification = None

        self.refresh_folder_list()

    def refresh_folder_list(self):
        counts = self.model.get_folder_counts()
        current_item = self.folder_list.currentItem()
        selected_name = current_item.text().split(" (")[0] if current_item else "Inbox"

        self.folder_list.clear()

        total_items = sum(counts.values())
        self.folder_list.addItem(f"All ({total_items})")

        std_folders = ["Inbox", "Sent", "Drafts", "Spam", "Trash", "Archived"]
        for f in std_folders:
            c = counts.get(f, 0)
            if c > 0:
                self.folder_list.addItem(f"{f} ({c})")

        items = self.folder_list.findItems(selected_name, Qt.MatchFlag.MatchStartsWith)
        if items:
            self.folder_list.setCurrentItem(items[0])
            self.on_folder_changed(items[0])
        else:
            self.folder_list.setCurrentRow(0)

    def on_folder_changed(self, item):
        if not item: return
        folder_name = item.text().split(" (")[0]
        self.lbl_status.setText(f"Viewing: {folder_name}")
        self.model.set_filter(folder=folder_name)

    def on_search_changed(self, text):
        self.model.set_filter(search=text)

    def on_email_selected(self, index):
        key = self.model.get_key_at_row(index.row())
        if key is not None:
            html = self.parser.get_email_body(key)
            self.web_view.setHtml(html)

    def closeEvent(self, event):
        if self.loader_thread and self.loader_thread.isRunning():
            self.lbl_status.setText("Stopping background thread...")
            self.loader_thread.stop()
            self.loader_thread.wait()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MailApp()
    window.show()
    sys.exit(app.exec())
