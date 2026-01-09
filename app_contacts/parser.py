import vobject


class ContactParser:
    @staticmethod
    def parse_vcf(file_path):
        contacts = []
        try:
            # Use 'utf-8' and handle errors to prevent crashes on bad characters
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                for vcard in vobject.readComponents(f):
                    contact = {
                        "name": "Unknown",
                        "email": [],
                        "phone": [],
                        "org": ""
                    }

                    # --- Extract Name (Improved Logic) ---
                    # 1. Try 'fn' (Formatted Name) first
                    if hasattr(vcard, 'fn') and vcard.fn.value.strip():
                        contact["name"] = vcard.fn.value.strip()

                    # 2. Fallback: Construct from 'n' (Name components) if 'fn' is missing/empty
                    # This fixes issues with non-English names that lack a formatted string
                    if (contact["name"] == "Unknown" or not contact["name"]) and hasattr(vcard, 'n'):
                        n_obj = vcard.n.value

                        # Safely get given and family names
                        given = n_obj.given.strip() if n_obj.given else ""
                        family = n_obj.family.strip() if n_obj.family else ""

                        # Combine them
                        full_name = f"{given} {family}".strip()
                        if full_name:
                            contact["name"] = full_name

                    # --- Extract Emails ---
                    if hasattr(vcard, 'email'):
                        email_list = vcard.contents.get('email', [])
                        for e in email_list:
                            contact["email"].append(e.value)

                    # --- Extract Phones ---
                    if hasattr(vcard, 'tel'):
                        tel_list = vcard.contents.get('tel', [])
                        for t in tel_list:
                            # Default to 'Mobile' if type is missing
                            t_type = t.params.get('TYPE', ['Mobile'])[0]
                            contact["phone"].append((t_type, t.value))

                    # --- Extract Organization ---
                    if hasattr(vcard, 'org'):
                        # .org.value might be a list or string depending on the parser
                        org_val = vcard.org.value
                        if isinstance(org_val, list) and org_val:
                            contact["org"] = org_val[0]
                        elif isinstance(org_val, str):
                            contact["org"] = org_val

                    contacts.append(contact)

            # Sort contacts alphabetically by name
            contacts.sort(key=lambda x: x['name'].lower())
            return contacts

        except Exception as e:
            print(f"Error parsing VCF: {e}")
            return []
