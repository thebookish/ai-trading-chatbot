import re
from typing import Dict, Any

PRICE_RE = re.compile(r"(price|level|market\s*value|value)\s+of\s+(?P<sym>[A-Za-z0-9^._-]+)", re.I)
ADD_TRADE_RE = re.compile(r"(buy|sell)\s+(?P<qty>[0-9.]+)\s+(?P<sym>[A-Za-z0-9^._-]+)\s+@\s*(?P<price>[0-9.]+)", re.I)
MARK_EXEC_RE = re.compile(r"(mark|set)\s+trade\s+(?P<id>\d+)\s+(executed|done)", re.I)
CANCEL_RE = re.compile(r"(cancel|remove|delete)\s+trade\s+(?P<id>\d+)", re.I)
LIST_TRADES_RE = re.compile(r"(list|show)\s+(open\s+)?trades", re.I)

SYMBOL_WORD_RE = re.compile(r"what\s+is\s+the\s+(current\s+)?(price|value|level)\s+of\s+(?P<sym>[A-Za-z0-9^._-]+)\??", re.I)


def parse_intent(text: str) -> Dict[str, Any]:
    t = text.strip()
    m = PRICE_RE.search(t) or SYMBOL_WORD_RE.search(t)
    if m:
        return {"intent": "price", "symbol": m.group("sym").upper()}
    m = ADD_TRADE_RE.search(t)
    if m:
        side = "buy" if t.lower().startswith("buy") else "sell"
        return {"intent": "add_trade", "side": side, "quantity": float(m.group("qty")), "symbol": m.group("sym").upper(), "price": float(m.group("price"))}
    m = MARK_EXEC_RE.search(t)
    if m:
        return {"intent": "mark_executed", "id": int(m.group("id"))}
    m = CANCEL_RE.search(t)
    if m:
        return {"intent": "cancel_trade", "id": int(m.group("id"))}
    m = LIST_TRADES_RE.search(t)
    if m:
        return {"intent": "list_trades"}
    return {"intent": "unknown"}
