from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QCalendarWidget,
                             QLabel, QListWidget, QListWidgetItem, QSplitter,
                             QFrame, QTextBrowser)
from PyQt6.QtCore import Qt, QDate, QLocale  # Added QLocale
from PyQt6.QtGui import QColor, QFont, QTextCharFormat, QBrush


class CustomCalendarWidget(QCalendarWidget):
    """
    Subclass to allow highlighting specific dates.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighted_dates = set()

        # FORCE ENGLISH LOCALE
        self.setLocale(QLocale(QLocale.Language.English))

        self.setNavigationBarVisible(True)
        self.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)

    def set_event_dates(self, date_strings):
        self.highlighted_dates = set(date_strings)
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QBrush(QColor("#e6f4ff")))
        highlight_format.setFontWeight(QFont.Weight.Bold)
        highlight_format.setForeground(QBrush(QColor("#0078d7")))

        for date_str in date_strings:
            qdate = QDate.fromString(date_str, "yyyy-MM-dd")
            self.setDateTextFormat(qdate, highlight_format)


class CalendarViewerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calendar Viewer")
        self.resize(1000, 800)  # Increased height slightly for the new row
        self.setup_ui()

    def setup_ui(self):
        # MAIN LAYOUT: Vertical to stack Splitter (Top) and Recent List (Bottom)
        main_layout = QVBoxLayout(self)

        # --- TOP SECTION: Splitter (Calendar + Agenda) ---
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 1. Left Panel: Calendar
        self.calendar = CustomCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setStyleSheet("""
            QCalendarWidget QWidget { alternate-background-color: #f9f9f9; }
            QAbstractItemView:enabled { font-size: 14px; color: #333; }
        """)
        splitter.addWidget(self.calendar)

        # 2. Right Panel: Daily Agenda
        self.right_panel = QWidget()
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(15, 15, 15, 15)

        self.lbl_date_header = QLabel("Select a Date")
        self.lbl_date_header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.lbl_date_header.setStyleSheet("color: #333; margin-bottom: 10px;")
        right_layout.addWidget(self.lbl_date_header)

        self.event_list = QListWidget()
        self.event_list.setStyleSheet("""
            QListWidget { border: 1px solid #ddd; background: white; border-radius: 4px;}
            QListWidget::item { padding: 8px; border-bottom: 1px solid #eee; }
            QListWidget::item:selected { background: #0078d7; color: white; }
        """)
        right_layout.addWidget(self.event_list)

        self.detail_text = QTextBrowser()
        self.detail_text.setStyleSheet("background: #fdfdfd; border: 1px solid #ddd; color: #444;")
        self.detail_text.setPlaceholderText("Event details will appear here... Click to view details...")
        right_layout.addWidget(self.detail_text)

        right_layout.setStretch(1, 2)
        right_layout.setStretch(2, 1)
        splitter.addWidget(self.right_panel)
        splitter.setSizes([600, 400])

        # Add the splitter to the main vertical layout
        main_layout.addWidget(splitter)

        # --- BOTTOM SECTION: Recent / All Events List ---
        bottom_container = QWidget()
        bottom_layout = QVBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0, 10, 0, 0)

        lbl_recent = QLabel("All Events (Sorted Chronologically)")
        lbl_recent.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        bottom_layout.addWidget(lbl_recent)

        self.recent_list = QListWidget()
        self.recent_list.setFixedHeight(200)  # Fixed height so it doesn't take over
        self.recent_list.setStyleSheet("""
            QListWidget { border: 1px solid #bdc3c7; background: #fdfdfd; }
            QListWidget::item { padding: 5px; }
            QListWidget::item:hover { background: #ecf0f1; }
        """)
        bottom_layout.addWidget(self.recent_list)

        main_layout.addWidget(bottom_container)

        # Set stretch: Splitter takes 3 parts, Bottom list takes 1 part
        main_layout.setStretch(0, 3)
        main_layout.setStretch(1, 1)
