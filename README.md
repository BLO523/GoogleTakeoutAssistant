# GoogleTakeoutAssistant
A standalone desktop GUI suite built with PyQt6 for offline browsing, searching, and visualizing Google Takeout exports, including MBOX emails, ICS calendars, and VCF contacts.

A Python-based application that helps you browse and inspect data exported from **Google Takeout**.  
It provides a unified dashboard to launch dedicated viewers for:

- Mail (`.mbox`)
- Calendar (`.ics`)
- Contacts (`.vcf`)

The app is built with **PyQt6**, supports large archives, and aims to stay responsive even with big mailboxes.

---

## Features

### 1. Mail Viewer (Pro Mail Viewer)

- **Large File Support**  
  - Uses threaded / chunked loading to handle large `.mbox` files.
  - Keeps the UI responsive while messages are being parsed.

- **Rich Content Rendering**  
  - Renders HTML emails using `QWebEngineView`.
  - Supports inline images and formatted content where available.

- **Smart Organization**  
  - Groups emails by Gmail-style labels/folders (Inbox, Sent, Trash, etc.) when available in the Takeout export.

- **Search & Filter**  
  - Real-time search by subject, sender, or other basic fields.
  - Sidebar/category filters to quickly narrow down what you see.

---

### 2. Calendar Viewer

- **Visual Calendar**  
  - Custom calendar view that highlights days with events.
  - Quickly see which days contain activity.

- **Event Details**  
  - Shows event title, start/end times, location, and description.
  - Supports multi-day and recurring events (as present in the data).

- **ICS Parsing**  
  - Uses the `vobject` library to parse standard `.ics` calendar files from Google Takeout.

---

### 3. Contact Viewer

- **VCF Parsing**  
  - Reads `.vcf` (vCard) contact files.
  - Extracts names, emails, phone numbers, organizations, and more when available.

- **Detailed Interface**  
  - Split-view layout:
    - Left: searchable list of contacts.
    - Right: detailed card for the selected contact.

- **Robust Handling**  
  - Fallback logic for:
    - Non-English names.
    - Different vCard versions and slightly inconsistent export formats.

---

## Tech Stack

- **Language:** Python 3.10+
- **GUI:** PyQt6
- **Parsing:**
  - `vobject` for `.ics` and `.vcf`
  - Python standard `mailbox` / `email` modules for `.mbox`

---

## Prerequisites

- Python **3.10 or newer**
- Recommended OS: Windows, macOS, or Linux with a working Python toolchain

### Required Python Packages

- `PyQt6`
- `PyQt6-WebEngine` (for HTML mail rendering, if not included in your PyQt6 install)
- `vobject`

