from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
from ..services import nlp
from ..services.market_data import get_provider
from ..services.trades import trade_service

router = APIRouter(prefix="/ask", tags=["ask"]) 

class AskIn(BaseModel):
    message: str

@router.post("")
async def ask(payload: AskIn) -> Dict[str, Any]:
    parsed = nlp.parse_intent(payload.message)
    intent = parsed.get("intent")

    if intent == "price":
        provider = await get_provider()
        try:
            q = await provider.get_price(parsed["symbol"])
            answer = f"{parsed['symbol']} is {q.price:.2f} {q.currency or ''} (provider: {q.provider_symbol})."
            return {"answer": answer, "intent": intent, "data": {"symbol": q.symbol, "price": q.price, "currency": q.currency, "provider_symbol": q.provider_symbol}}
        except Exception as e:
            raise HTTPException(404, detail=str(e))

    if intent == "add_trade":
        t = trade_service.create(symbol=parsed["symbol"], side=parsed["side"], quantity=parsed["quantity"], price=parsed["price"]) 
        return {"answer": f"Added trade #{t.id}: {t.side} {t.quantity} {t.symbol} @ {t.price}", "intent": intent, "data": t.model_dump()}

    if intent == "mark_executed":
        try:
            t = trade_service.update(parsed["id"], status="executed")
            return {"answer": f"Trade #{t.id} marked executed.", "intent": intent, "data": t.model_dump()}
        except ValueError:
            raise HTTPException(404, detail="trade_not_found")

    if intent == "cancel_trade":
        try:
            trade_service.delete(parsed["id"])
            return {"answer": f"Trade #{parsed['id']} removed.", "intent": intent, "data": {"id": parsed['id']}}
        except ValueError:
            raise HTTPException(404, detail="trade_not_found")

    if intent == "list_trades":
        trades = [t.model_dump() for t in trade_service.list() if t.status != "executed"]
        return {"answer": f"{len(trades)} open trades.", "intent": intent, "data": trades}

    return {"answer": "Sorry, I couldn't infer your request. Try: 'price of SX5E', 'buy 10 SX5E @ 4200', 'mark trade 3 executed'.", "intent": "unknown", "data": {}}
