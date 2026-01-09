from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableView,
                             QSplitter, QLabel, QLineEdit, QListWidget,
                             QAbstractItemView, QProgressBar)  # Added QProgressBar
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt


class MailViewerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pro Mail Viewer (Stable)")
        self.resize(1200, 800)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # --- TOP BAR (Search) ---
        top_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search sender or subject...")
        self.search_input.setClearButtonEnabled(True)
        top_bar.addWidget(QLabel("Search:"))
        top_bar.addWidget(self.search_input)
        main_layout.addLayout(top_bar)

        # --- MAIN SPLITTER ---
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # 1. Folder List
        self.folder_list = QListWidget()
        self.folder_list.setMaximumWidth(200)
        main_splitter.addWidget(self.folder_list)

        # 2. Content Splitter
        content_splitter = QSplitter(Qt.Orientation.Vertical)

        self.mail_table = QTableView()
        self.mail_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.mail_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.mail_table.setShowGrid(False)
        self.mail_table.setAlternatingRowColors(True)
        self.mail_table.verticalHeader().setVisible(False)
        content_splitter.addWidget(self.mail_table)

        self.web_view = QWebEngineView()
        content_splitter.addWidget(self.web_view)

        main_splitter.addWidget(content_splitter)
        main_splitter.setSizes([150, 350, 500])
        main_layout.addWidget(main_splitter)

        # --- BOTTOM BAR (Status + Progress) ---
        bottom_layout = QHBoxLayout()

        self.lbl_status = QLabel("Ready")
        bottom_layout.addWidget(self.lbl_status)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)  # Hidden by default
        bottom_layout.addWidget(self.progress_bar)

        main_layout.addLayout(bottom_layout)
