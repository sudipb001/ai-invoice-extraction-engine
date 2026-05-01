SYMBOL_MAP = {
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
    "₹": "INR",
    "Rs": "INR",
    "Rs.": "INR",
    "¥": "JPY",
}


def normalize_currency(value: str | None) -> str | None:
    if not value:
        return None

    value = value.strip()

    return SYMBOL_MAP.get(value, value.upper())
