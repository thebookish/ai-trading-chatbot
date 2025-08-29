    # Backend notes
- Set `DATA_PROVIDER=mock` to run without internet.
- Supported intents:
  - `what is the price/value/level of <SYMBOL>` or `price of <SYMBOL>`
  - `buy <QTY> <SYMBOL> @ <PRICE>` / `sell ...`
  - `list trades`
  - `mark trade <ID> executed`
  - `cancel trade <ID>`
- Symbol map lives in `app/services/market_data.py` (e.g., SX5E→^STOXX50E).
