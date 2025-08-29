from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..services.trades import trade_service

router = APIRouter(prefix="/trades", tags=["trades"]) 

class TradeIn(BaseModel):
    symbol: str
    side: str
    quantity: float
    price: float
    note: Optional[str] = None

class TradePatch(BaseModel):
    symbol: Optional[str] = None
    side: Optional[str] = None
    quantity: Optional[float] = None
    price: Optional[float] = None
    status: Optional[str] = None
    note: Optional[str] = None

@router.get("")
def get_trades():
    return [t.model_dump() for t in trade_service.list()]

@router.post("")
def create_trade(payload: TradeIn):
    t = trade_service.create(**payload.model_dump())
    return t.model_dump()

@router.patch("/{trade_id}")
def update_trade(trade_id: int, payload: TradePatch):
    try:
        t = trade_service.update(trade_id, **{k:v for k,v in payload.model_dump().items() if v is not None})
        return t.model_dump()
    except ValueError:
        raise HTTPException(404, "trade_not_found")

@router.delete("/{trade_id}")
def delete_trade(trade_id: int):
    try:
        trade_service.delete(trade_id)
        return {"ok": True}
    except ValueError:
        raise HTTPException(404, "trade_not_found")
