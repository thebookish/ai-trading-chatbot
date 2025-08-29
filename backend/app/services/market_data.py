from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple, Optional
import os
import time
import threading
import json

from ..utils.text import normalize_symbol
from ..config import settings

# --------------------------------------------------------------------
# Logical symbols -> provider candidates (used by Yahoo & for /symbols)
# --------------------------------------------------------------------
CANDIDATES: dict[str, List[Tuple[str, str]]] = {
    # (provider_symbol, note)
    "SX5E": [("^STOXX50E", "Yahoo index primary"),
             ("^STOXX50",  "Yahoo index alt"),
             ("FEZ",       "ETF proxy: SPDR EURO STOXX 50"),
             ("EZU",       "ETF proxy: iShares MSCI EMU")],
    "SX7E": [("^SX7E", "Yahoo index primary")],
    "DAX":  [("^GDAXI", "Yahoo index primary"),
             ("DAX",    "ETF proxy: iShares DAX")],
    "CAC":  [("^FCHI", "Yahoo index primary")],
    "IBEX": [("^IBEX", "Yahoo index primary")],
    "AEX":  [("^AEX",  "Yahoo index primary")],
    "FTSE": [("^FTSE", "Yahoo index primary")],
    "SMI":  [("^SSMI", "Yahoo index primary")],
    "MIB":  [("FTSEMIB.MI", "Yahoo index primary")],
    "SPX":  [("^GSPC", "Yahoo index primary"), ("SPY", "ETF proxy")],
    "NDX":  [("^NDX",  "Yahoo index primary"), ("QQQ", "ETF proxy")],
}

# ---------------------------
# Simple in-memory cache
# ---------------------------
class TTLCache:
    def __init__(self, ttl_seconds: float = 45.0):
        self.ttl = ttl_seconds
        self._data: Dict[str, Tuple[float, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        now = time.time()
        with self._lock:
            item = self._data.get(key)
            if not item:
                return None
            ts, value = item
            if now - ts > self.ttl:
                self._data.pop(key, None)
                return None
            return value

    def set(self, key: str, value: Any):
        with self._lock:
            self._data[key] = (time.time(), value)

_cache = TTLCache(ttl_seconds=45.0)

# ---------------------------
# Data structures
# ---------------------------
@dataclass
class Quote:
    symbol: str              # logical (e.g., SX5E)
    provider_symbol: str     # actual symbol/provider (e.g., ^STOXX50E, openai:SX5E)
    price: float
    currency: str | None
    raw: Dict[str, Any] | None = None
    note: str | None = None

class MarketDataProvider:
    async def get_price(self, symbol: str) -> Quote:
        raise NotImplementedError

# ---------------------------
# Mock provider
# ---------------------------
class MockProvider(MarketDataProvider):
    async def get_price(self, symbol: str) -> Quote:
        s = normalize_symbol(symbol)
        ck = f"mock:{s}"
        cached = _cache.get(ck)
        if cached:
            return cached
        q = Quote(symbol=s, provider_symbol=s, price=1234.56, currency="USD", raw={"source": "mock"}, note="mock")
        _cache.set(ck, q)
        return q

# ---------------------------
# Yahoo provider (yfinance)
# ---------------------------
def _try_one_yf_symbol(yf_symbol: str, retries: int = 2, backoff: float = 1.2):
    import yfinance as yf
    import pandas as pd  # noqa: F401

    last_err = None
    for i in range(retries):
        try:
            t = yf.Ticker(yf_symbol)

            # 1) fast_info
            try:
                fi = t.fast_info
                price = fi.get("lastPrice") or fi.get("last_price") or fi.get("regularMarketPrice")
                currency = fi.get("currency")
                if price:
                    return float(price), currency
            except Exception as e:
                last_err = e

            # 2) info
            try:
                info = t.info or {}
                price = info.get("regularMarketPrice") or info.get("previousClose")
                currency = info.get("currency") or info.get("financialCurrency")
                if price:
                    return float(price), currency
            except Exception as e:
                last_err = e

            # 3) light history
            try:
                hist = yf.download(yf_symbol, period="5d", interval="1h",
                                   progress=False, group_by="ticker", auto_adjust=False)
                if hasattr(hist, "empty") and not hist.empty:
                    if "Close" in hist.columns:
                        series = hist["Close"].dropna()
                    elif (yf_symbol, "Close") in hist.columns:
                        series = hist[(yf_symbol, "Close")].dropna()
                    else:
                        series = hist.iloc[:, 0].dropna()
                    if not series.empty:
                        return float(series.iloc[-1]), None
            except Exception as e:
                last_err = e

        except Exception as e:
            last_err = e

        time.sleep(backoff * (i + 1))

    raise last_err or RuntimeError(f"No data for {yf_symbol}")

class YFinanceProvider(MarketDataProvider):
    async def get_price(self, symbol: str) -> Quote:
        s = normalize_symbol(symbol)
        ck = f"yf:{s}"
        cached = _cache.get(ck)
        if cached:
            return cached

        candidates = CANDIDATES.get(s, [(s, "as-is")])
        last_err = None
        for yf_symbol, note in candidates:
            try:
                price, currency = _try_one_yf_symbol(yf_symbol)
                q = Quote(symbol=s, provider_symbol=yf_symbol, price=price, currency=currency, note=note)
                _cache.set(ck, q)
                return q
            except Exception as e:
                last_err = e
        raise RuntimeError(f"No data found for {symbol}: {last_err}")

# ---------------------------
# OpenAI provider (JSON mode)
# ---------------------------
# Requires: pip install openai>=1.40.0
# Env: OPENAI_API_KEY, optional MODEL_NAME in settings (default 'gpt-4o-mini')
class OpenAIProvider(MarketDataProvider):
    def __init__(self, api_key: str, model: str | None = None):
        # OpenAI SDK v1
        try:
            from openai import OpenAI  # type: ignore
        except Exception as e:  # pragma: no cover
            raise RuntimeError("OpenAI SDK not installed. Run `pip install openai>=1.40.0`.") from e
        self.OpenAI = OpenAI
        self.api_key = api_key
        self.model = model or getattr(settings, "MODEL_NAME", "gpt-4o-mini")

    def _client(self):
        return self.OpenAI(api_key=self.api_key)

    def _json_price_prompt(self, logical_symbol: str) -> list[dict]:
        # Keep it extremely constrained; ask for number and optional currency.
        return [
            {"role": "system", "content": (
                "You are a financial data retriever. "
                "Return ONLY valid JSON with keys: 'price' (float) and 'currency' (string or null). "
                "Do not include any other keys or text."
            )},
            {"role": "user", "content": (
                f"Find the latest market level (most recent price) of {logical_symbol}. "
                "Use a reputable public source. Output strictly as JSON."
            )},
        ]

    @staticmethod
    def _coerce_price_currency(payload: str) -> tuple[float, Optional[str]]:
        """
        Strictly parse JSON; fallback to regex extraction if needed.
        """
        # Try JSON first
        try:
            data = json.loads(payload)
            price = float(data["price"])
            currency = data.get("currency")
            if isinstance(currency, str):
                currency = currency.strip() or None
            else:
                currency = None
            return price, currency
        except Exception:
            # Fallback: extract first number from free text
            import re
            m = re.search(r"([0-9][0-9,_.]*)", payload)
            if not m:
                raise RuntimeError(f"Could not parse price from LLM response: {payload!r}")
            num = m.group(1).replace(",", "").replace("_", "")
            price = float(num)
            cur = None
            m2 = re.search(r"\b(USD|EUR|GBP|CHF)\b", payload, re.IGNORECASE)
            if m2:
                cur = m2.group(1).upper()
            return price, cur

    async def get_price(self, symbol: str) -> Quote:
        s = normalize_symbol(symbol)
        ck = f"openai:{s}"
        cached = _cache.get(ck)
        if cached:
            return cached

        client = self._client()

        # JSON mode
        try:
            resp = client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=self._json_price_prompt(s),
                temperature=0,
            )
            content = resp.choices[0].message.content or ""
        except Exception as e:
            # If JSON mode not supported or rate limited, try plain completion
            resp = client.chat.completions.create(
                model=self.model,
                messages=self._json_price_prompt(s),
                temperature=0,
            )
            content = resp.choices[0].message.content or ""

        price, currency = self._coerce_price_currency(content)
        q = Quote(symbol=s, provider_symbol=f"openai:{s}", price=price, currency=currency, note="via OpenAI (web/general knowledge)")
        _cache.set(ck, q)
        return q

# ---------------------------
# Provider factory
# ---------------------------
async def get_provider() -> MarketDataProvider:
    provider = settings.DATA_PROVIDER.lower()
    if provider == "mock":
        return MockProvider()
    if provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY") or getattr(settings, "OPENAI_API_KEY", None)
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set; cannot use DATA_PROVIDER=openai")
        return OpenAIProvider(api_key=api_key, model=getattr(settings, "MODEL_NAME", "gpt-4o-mini"))
    # default
    return YFinanceProvider()
