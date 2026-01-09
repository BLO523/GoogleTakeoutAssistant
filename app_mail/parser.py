import mailbox
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
import base64
import threading


class MboxParser:
    def __init__(self):
        self.mbox = None
        self.filepath = None
        # This lock ensures only one thread touches the file at a time
        self.lock = threading.RLock()

    def load_mbox(self, filepath):
        with self.lock:
            self.filepath = filepath
            # factory=None is faster/safer for just reading raw bytes later
            self.mbox = mailbox.mbox(filepath, factory=None)
            return len(self.mbox)

    def get_headers_generator(self):
        keys = []
        with self.lock:
            if not self.mbox: return
            try:
                keys = self.mbox.keys()
            except Exception:
                return

        for key in keys:
            try:
                # 1. READ DATA (Thread Safe)
                with self.lock:
                    msg_proxy = self.mbox.get_message(key)
                    # Convert to email object immediately to detach from file
                    # so we don't hold the lock during parsing
                    msg_bytes = msg_proxy.as_bytes()

                # 2. PARSE DATA (No Lock needed here, purely memory CPU work)
                msg = email.message_from_bytes(msg_bytes)

                subject = self._decode_str(msg['subject'] or "(No Subject)")[:100]
                sender = self._decode_str(msg['from'] or "Unknown")[:100]

                date_str = msg['date']
                display_date = str(date_str)[:20] if date_str else ""
                try:
                    if date_str:
                        dt = parsedate_to_datetime(date_str)
                        display_date = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    pass

                # Categorization
                labels = msg.get('X-Gmail-Labels', '').lower()
                folder = "Inbox"
                if 'sent' in labels:
                    folder = "Sent"
                elif 'trash' in labels or 'bin' in labels:
                    folder = "Trash"
                elif 'spam' in labels:
                    folder = "Spam"
                elif 'draft' in labels:
                    folder = "Drafts"
                elif 'archived' in labels:
                    folder = "Archived"

                yield (key, sender, subject, display_date, folder)

            except Exception:
                continue

    def get_email_body(self, key):
        try:
            with self.lock:
                if not self.mbox: return ""
                msg_proxy = self.mbox.get_message(key)
                msg_bytes = msg_proxy.as_bytes()

            # Parsing happens after lock is released
            email_msg = email.message_from_bytes(msg_bytes)
            return self._process_body_and_images(email_msg)
        except Exception as e:
            return f"<h3>Error reading email</h3><p>{str(e)}</p>"

    def _process_body_and_images(self, msg):
        html_body = ""
        text_body = ""
        images = {}

        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if content_type.startswith("image/"):
                cid = part.get("Content-ID")
                if cid:
                    cid = cid.strip('<>')
                    img_data = part.get_payload(decode=True)
                    if img_data:
                        b64_img = base64.b64encode(img_data).decode('utf-8')
                        images[cid] = f"data:{content_type};base64,{b64_img}"
                continue

            if "attachment" not in content_disposition:
                try:
                    payload = part.get_payload(decode=True)
                    if not payload: continue
                    charset = part.get_content_charset() or 'utf-8'
                    decoded = payload.decode(charset, errors='replace')

                    if content_type == "text/html":
                        html_body = decoded
                    elif content_type == "text/plain":
                        text_body = decoded
                except:
                    pass

        final_html = html_body if html_body else f"<pre>{text_body}</pre>"
        for cid, b64_src in images.items():
            final_html = final_html.replace(f"cid:{cid}", b64_src)
        return final_html

    def _decode_str(self, header_value):
        if not header_value: return ""
        try:
            parts = []
            for bytes_content, encoding in decode_header(header_value):
                if isinstance(bytes_content, bytes):
                    parts.append(bytes_content.decode(encoding or 'utf-8', errors='replace'))
                else:
                    parts.append(str(bytes_content))
            return "".join(parts)
        except:
            return str(header_value)
