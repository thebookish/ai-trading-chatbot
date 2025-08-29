# AI Trading Chatbot
Python FastAPI backend + React/Tailwind frontend for a lightweight trading assistant.

## Features
- Ask: “price/value of SX5E” (and other indices)
- Manage trades: add, list, mark executed, delete (via chat or UI table)
- Pluggable market data provider (`yfinance` by default, `mock` available)

## Quickstart
### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
### Frontend
```bash
cd ../frontend
npm install
npm run dev
```
Open http://localhost:5173
