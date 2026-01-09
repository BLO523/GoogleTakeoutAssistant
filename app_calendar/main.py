import sys
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox, QListWidgetItem
from PyQt6.QtCore import QDate

try:
    # Case 1: Running directly
    from parser import CalendarParser
    from ui_layout import CalendarViewerUI
except ImportError:
    # Case 2: Running from root (FIXED DOT NOTATION)
    from app_calendar.parser import CalendarParser
    from app_calendar.ui_layout import CalendarViewerUI


class CalendarApp(CalendarViewerUI):
    def __init__(self):
        super().__init__()
        self.events_data = {}

        # Connect Signals
        self.calendar.clicked.connect(self.on_date_clicked)
        self.event_list.itemClicked.connect(self.on_event_selected)

        # NEW: Connect the bottom "Recent" list to jump to date
        self.recent_list.itemClicked.connect(self.on_recent_item_clicked)

        # Auto-load
        self.load_file_dialog()

    def load_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Google Calendar ICS", "", "ICS Files (*.ics);;All Files (*)"
        )
        if file_path:
            self.load_calendar(file_path)

    def load_calendar(self, path):
        self.setWindowTitle("Calendar Viewer - Loading...")
        QApplication.processEvents()

        self.events_data = CalendarParser.parse_ics(path)

        if not self.events_data:
            self.setWindowTitle("Calendar Viewer")
            QMessageBox.warning(self, "Error", "No events found or failed to parse.")
            return

        self.calendar.set_event_dates(self.events_data.keys())
        self.setWindowTitle(f"Calendar Viewer - {len(self.events_data)} Days with Events")

        # Select today or first available
        today_str = QDate.currentDate().toString("yyyy-MM-dd")
        if today_str in self.events_data:
            self.calendar.setSelectedDate(QDate.currentDate())
            self.on_date_clicked(QDate.currentDate())

        # NEW: Populate the bottom list
        self.populate_all_events_list()

    def populate_all_events_list(self):
        """Flattens the event dictionary and shows all events sorted by time."""
        self.recent_list.clear()

        # 1. Flatten all events into a single list
        all_events = []
        for day_events in self.events_data.values():
            all_events.extend(day_events)

        # 2. Sort by start date
        all_events.sort(key=lambda x: x['start_dt'])

        # 3. Add to list widget
        for evt in all_events:
            start_str = evt['start_dt'].strftime("%Y-%m-%d %H:%M")
            label = f"{start_str} | {evt['summary']}"

            item = QListWidgetItem(label)
            item.setData(100, evt)  # Store event object
            self.recent_list.addItem(item)

    def on_date_clicked(self, qdate):
        """Update the list widget with events for this day"""
        date_str = qdate.toString("yyyy-MM-dd")
        pretty_date = qdate.toString("dddd, MMMM d, yyyy")
        self.lbl_date_header.setText(pretty_date)

        self.event_list.clear()
        self.detail_text.clear()

        events = self.events_data.get(date_str, [])

        if not events:
            item = QListWidgetItem("(No events)")
            item.setFlags(item.flags() & ~sys.modules['PyQt6.QtCore'].Qt.ItemFlag.ItemIsEnabled)
            self.event_list.addItem(item)
            return

        for evt in events:
            if evt['is_all_day']:
                time_str = "All Day"
            else:
                time_str = evt['start_dt'].strftime("%H:%M")

            label_text = f"[{time_str}] {evt['summary']}"
            item = QListWidgetItem(label_text)
            item.setData(100, evt)
            self.event_list.addItem(item)

    def on_event_selected(self, item):
        """Show full details in the detail box (Right Panel)"""
        evt = item.data(100)
        if not evt: return
        self._display_event_details(evt)

    def on_recent_item_clicked(self, item):
        """When clicking an event in the bottom list, jump to that date"""
        evt = item.data(100)
        if not evt: return

        # 1. Show details
        self._display_event_details(evt)

        # 2. Jump Calendar to that date
        # Note: start_dt might be datetime or date object
        if hasattr(evt['start_dt'], 'date'):
            py_date = evt['start_dt'].date()
        else:
            py_date = evt['start_dt']

        qdate = QDate(py_date.year, py_date.month, py_date.day)
        self.calendar.setSelectedDate(qdate)

        # 3. Refresh the daily view
        self.on_date_clicked(qdate)

    def _display_event_details(self, evt):
        html = f"""
        <h3>{evt['summary']}</h3>
        <p><b>Time:</b> {evt['start_dt']} - {evt['end_dt']}</p>
        <p><b>Location:</b> {evt['location']}</p>
        <hr>
        <p>{evt['description'].replace(chr(10), '<br>')}</p>
        """
        self.detail_text.setHtml(html)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CalendarApp()
    window.show()
    sys.exit(app.exec())
