from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                             QLabel, QSplitter, QFrame, QScrollArea, QListWidgetItem)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor


class ContactViewerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Contact Viewer")
        self.resize(900, 600)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # --- Splitter (Left: List, Right: Details) ---
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 1. Left Sidebar (Contact List)
        self.left_panel = QWidget()
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)

        # Search Bar Placeholder (Logic can be added later)
        self.search_label = QLabel("Contacts")
        self.search_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        left_layout.addWidget(self.search_label)

        self.contact_list = QListWidget()
        self.contact_list.setAlternatingRowColors(True)
        # Style the list slightly
        self.contact_list.setStyleSheet("""
            QListWidget { border: none; background: #f5f5f5; }
            QListWidget::item { padding: 10px; border-bottom: 1px solid #e0e0e0; }
            QListWidget::item:selected { background: #0078d7; color: white; }
        """)
        left_layout.addWidget(self.contact_list)

        # 2. Right Panel (Details)
        self.right_panel = QScrollArea()
        self.right_panel.setWidgetResizable(True)
        self.right_panel.setStyleSheet("QScrollArea {border: none; background: white;}")

        self.details_container = QWidget()
        self.details_container.setStyleSheet("background: white;")
        self.details_layout = QVBoxLayout(self.details_container)
        self.details_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.details_layout.setContentsMargins(40, 40, 40, 40)

        # Define Detail Widgets (Empty initially)
        self.lbl_avatar = QLabel("No Selection")
        self.lbl_avatar.setFixedSize(100, 100)
        self.lbl_avatar.setStyleSheet("background-color: #ddd; border-radius: 50px; qproperty-alignment: AlignCenter;")

        self.lbl_name = QLabel("")
        self.lbl_name.setFont(QFont("Arial", 24, QFont.Weight.Bold))

        self.lbl_org = QLabel("")
        self.lbl_org.setStyleSheet("color: gray; font-size: 14px;")

        # Add to layout
        self.details_layout.addWidget(self.lbl_avatar, alignment=Qt.AlignmentFlag.AlignCenter)
        self.details_layout.addWidget(self.lbl_name, alignment=Qt.AlignmentFlag.AlignCenter)
        self.details_layout.addWidget(self.lbl_org, alignment=Qt.AlignmentFlag.AlignCenter)
        self.details_layout.addSpacing(20)

        # Info Container (Dynamic area for phones/emails)
        self.info_area = QVBoxLayout()
        self.details_layout.addLayout(self.info_area)

        self.right_panel.setWidget(self.details_container)

        # Add panels to splitter
        splitter.addWidget(self.left_panel)
        splitter.addWidget(self.right_panel)
        splitter.setSizes([250, 650])  # Initial widths

        main_layout.addWidget(splitter)

    def update_details(self, contact_data):
        """Populates the right panel with data"""
        # clear previous info rows
        while self.info_area.count():
            child = self.info_area.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Update Header
        self.lbl_name.setText(contact_data['name'])
        self.lbl_org.setText(contact_data['org'])

        # Simple Avatar Logic (First letter of name)
        initial = contact_data['name'][0] if contact_data['name'] else "?"
        self.lbl_avatar.setText(initial)
        self.lbl_avatar.setStyleSheet(f"""
            QLabel {{
                background-color: #0078d7; 
                color: white; 
                border-radius: 50px; 
                font-size: 40px; 
                qproperty-alignment: AlignCenter;
            }}
        """)

        # Helper to create rows
        def add_row(label_text, value_text):
            row_widget = QWidget()
            row_layout = QVBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 5, 0, 15)

            lbl = QLabel(label_text.upper())
            lbl.setStyleSheet("color: #0078d7; font-weight: bold; font-size: 11px;")
            val = QLabel(value_text)
            val.setFont(QFont("Arial", 14))
            val.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

            row_layout.addWidget(lbl)
            row_layout.addWidget(val)
            self.info_area.addWidget(row_widget)

        # Add Phones
        for p_type, number in contact_data['phone']:
            add_row(f"Phone ({p_type})", number)

        # Add Emails
        for email in contact_data['email']:
            add_row("Email", email)
