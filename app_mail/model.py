from PyQt6.QtCore import QAbstractTableModel, Qt


class EmailTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self._all_data = []  # Master list
        self._display_data = []  # Filtered list shown in UI
        self._headers = ["Sender", "Subject", "Date"]

        # Filter States
        self.current_folder = "Inbox"
        self.search_text = ""

    def rowCount(self, parent=None):
        return len(self._display_data)

    def columnCount(self, parent=None):
        return len(self._headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None

        # Tuple: (key, sender, subject, date, folder)
        # Col 0->Sender(1), Col 1->Subject(2), Col 2->Date(3)
        row_data = self._display_data[index.row()]
        return row_data[index.column() + 1]

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._headers[section]
        return None

    def add_rows(self, new_rows):
        """Add rows to master list, then re-filter to see if they should show up."""
        self.beginResetModel()
        self._all_data.extend(new_rows)
        self._apply_filters()
        self.endResetModel()

    def set_filter(self, folder=None, search=None):
        """Update filter criteria and refresh view."""
        if folder is not None: self.current_folder = folder
        if search is not None: self.search_text = search.lower()

        self.beginResetModel()
        self._apply_filters()
        self.endResetModel()

    def _apply_filters(self):
        """Rebuilds _display_data based on folder and search text."""
        self._display_data = []

        for row in self._all_data:
            # Row structure: (key, sender, subject, date, folder)
            r_sender = row[1].lower()
            r_subject = row[2].lower()
            r_folder = row[4]

            # 1. Folder Check
            # If folder is "All", show everything, otherwise match folder name
            if self.current_folder != "All" and r_folder != self.current_folder:
                continue

            # 2. Search Check
            if self.search_text:
                if self.search_text not in r_sender and self.search_text not in r_subject:
                    continue

            self._display_data.append(row)

    def get_key_at_row(self, row_index):
        if 0 <= row_index < len(self._display_data):
            return self._display_data[row_index][0]
        return None

    def get_folder_counts(self):
        """Helper to update sidebar numbers (e.g. Inbox (5))"""
        counts = {}
        for row in self._all_data:
            f = row[4]
            counts[f] = counts.get(f, 0) + 1
        return counts

    def clear(self):
        self.beginResetModel()
        self._all_data = []
        self._display_data = []
        self.endResetModel()
