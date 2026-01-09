import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QFrame, QSpacerItem,
                             QSizePolicy, QMessageBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon, QAction

# FIXED IMPORTS (added dots between folder and module)
try:
    from app_contacts.main import ContactApp  # Added dot
    from app_calendar.main import CalendarApp  # Added dot
    from app_mail.main import MailApp  # Added dot
except ImportError as e:
    print(
        "Error importing sub-modules. Ensure folders 'app_contacts', 'app_calendar', and 'app_mail' exist with __init__.py files.")
    print(f"Details: {e}")
    sys.exit(1)


class DashboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Google Takeout Viewer Suite")
        self.resize(800, 600)

        # Central Widget setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(20)

        # --- HEADER SECTION ---
        header_label = QLabel("Google Takeout Viewer")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #2c3e50;")
        self.layout.addWidget(header_label)

        subheader_label = QLabel("Select a file type to view")
        subheader_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subheader_label.setFont(QFont("Segoe UI", 14))
        subheader_label.setStyleSheet("color: #7f8c8d; margin-bottom: 20px;")
        self.layout.addWidget(subheader_label)

        # --- BUTTONS SECTION ---
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(30)

        # 1. Contacts Button
        self.btn_contacts = self.create_launcher_button(
            "Contacts",
            "View .VCF files",
            "#3498db"
        )
        self.btn_contacts.clicked.connect(self.launch_contacts)
        buttons_layout.addWidget(self.btn_contacts)

        # 2. Calendar Button
        self.btn_calendar = self.create_launcher_button(
            "Calendar",
            "View .ICS files",
            "#27ae60"
        )
        self.btn_calendar.clicked.connect(self.launch_calendar)
        buttons_layout.addWidget(self.btn_calendar)

        # 3. Mail Button
        self.btn_mail = self.create_launcher_button(
            "Mail",
            "View .MBOX files",
            "#e74c3c"
        )
        self.btn_mail.clicked.connect(self.launch_mail)
        buttons_layout.addWidget(self.btn_mail)

        self.layout.addLayout(buttons_layout)
        self.layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # --- FOOTER SECTION ---
        footer_frame = QFrame()
        footer_frame.setStyleSheet("border-top: 1px solid #bdc3c7; margin-top: 20px;")
        footer_layout = QVBoxLayout(footer_frame)

        credits_label = QLabel("Created by BLO  |  hantang523@gmail.com  |  Helper: Google Gemini 3 Pro")
        credits_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credits_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        credits_label.setStyleSheet("color: #95a5a6; padding-top: 10px;")

        footer_layout.addWidget(credits_label)
        self.layout.addWidget(footer_frame)

    def create_launcher_button(self, title, subtitle, color):
        btn = QPushButton()
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(200)
        btn.setText(f"{title}\n{subtitle}")
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                border: 2px solid {color};
                border-radius: 15px;
                color: {color};
                font-size: 24px;
                font-weight: bold;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {color};
                color: white;
            }}
        """)
        return btn

    def launch_contacts(self):
        self.sub_window = ContactApp()
        self.sub_window.show()

    def launch_calendar(self):
        self.sub_window = CalendarApp()
        self.sub_window.show()

    def launch_mail(self):
        self.sub_window = MailApp()
        self.sub_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec())
