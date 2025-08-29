import re
def normalize_symbol(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9^._-]", "", text).upper()
