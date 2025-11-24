# utils.py
import csv
import io
from email_validator import validate_email, EmailNotValidError
import phonenumbers

def parse_csv_file(file_stream):
    """
    Accepts an uploaded file stream (bytes) and returns list of dicts.
    CSV columns expected: email, phone (but can be any order; header required)
    """
    text = file_stream.read().decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    rows = []
    for r in reader:
        rows.append({k.strip().lower(): (v.strip() if v else "") for k,v in r.items()})
    return rows

def validate_email_address(addr):
    if not addr:
        return False
    try:
        valid = validate_email(addr)
        return valid.email
    except EmailNotValidError:
        return False

def validate_phone_number(num, default_region=None):
    if not num:
        return False
    try:
        parsed = phonenumbers.parse(num, default_region)
        if phonenumbers.is_possible_number(parsed) and phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        return False
    except Exception:
        return False
