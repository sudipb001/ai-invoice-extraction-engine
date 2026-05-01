from app.config import PROCESSED_INVOICES_FILE
from app.utils.file_store import load_json, save_json


def is_duplicate(invoice: dict) -> bool:
    records = load_json(PROCESSED_INVOICES_FILE)

    key = (
        invoice.get("invoice_number"),
        invoice.get("vendor_name"),
        invoice.get("total_amount"),
    )

    for r in records:
        if (
            r.get("invoice_number"),
            r.get("vendor_name"),
            r.get("total_amount"),
        ) == key:
            return True

    return False


def register_invoice(invoice: dict):
    records = load_json(PROCESSED_INVOICES_FILE)

    records.append(invoice)

    records = records[-1000:]

    save_json(PROCESSED_INVOICES_FILE, records)
