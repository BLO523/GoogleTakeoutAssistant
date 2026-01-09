import vobject
from datetime import datetime, date


class CalendarParser:
    @staticmethod
    def parse_ics(file_path):
        """
        Parses ICS file and returns a dictionary:
        {
            '2023-10-27': [EventObj, EventObj],
            '2023-10-28': [EventObj]
        }
        """
        events_by_date = {}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # vobject.readComponents is a generator that yields top-level components
                # We need to iterate through VCALENDAR then VEVENT
                for calendar in vobject.readComponents(f):
                    for component in calendar.components():
                        if component.name == 'VEVENT':
                            event_data = CalendarParser._extract_event_data(component)

                            # Group by Start Date (YYYY-MM-DD string) for easy lookup
                            start_key = event_data['start_dt'].strftime('%Y-%m-%d')

                            if start_key not in events_by_date:
                                events_by_date[start_key] = []
                            events_by_date[start_key].append(event_data)

            # Sort events within each day by time
            for date_key in events_by_date:
                events_by_date[date_key].sort(key=lambda x: x['start_dt'])

            return events_by_date

        except Exception as e:
            print(f"Error parsing ICS: {e}")
            return {}

    @staticmethod
    def _extract_event_data(component):
        """Helper to extract safe values from a VEVENT component"""

        # Helper to safely get value
        def get_val(name):
            return component.contents[name][0].value if name in component.contents else ""

        # Handle Dates (DTSTART is mandatory in valid ICS, but good to be safe)
        start = component.dtstart.value if hasattr(component, 'dtstart') else datetime.now()
        end = component.dtend.value if hasattr(component, 'dtend') else start

        # Convert pure 'date' objects to 'datetime' for consistency if needed,
        # but for this viewer, keeping them as is usually fine.

        return {
            "summary": get_val('summary') or "(No Title)",
            "description": get_val('description'),
            "location": get_val('location'),
            "start_dt": start,
            "end_dt": end,
            "is_all_day": not isinstance(start, datetime)  # If it's just a date object, it's all-day
        }
