from ..models import Trade
from ..db import DBSession
from datetime import datetime
from typing import List

class TradeService:
        def list(self) -> List[Trade]:
            with DBSession() as s:
                return s.query(Trade).order_by(Trade.created_at.desc()).all()

        def create(self, *, symbol: str, side: str, quantity: float, price: float, note: str | None = None) -> Trade:
            t = Trade(symbol=symbol.upper(), side=side.lower(), quantity=quantity, price=price, note=note)
            with DBSession() as s:
                s.add(t)
                s.commit()
                s.refresh(t)
                return t

        def update(self, trade_id: int, **fields) -> Trade:
            with DBSession() as s:
                t = s.get(Trade, trade_id)
                if not t:
                    raise ValueError("trade_not_found")
                for k, v in fields.items():
                    setattr(t, k, v)
                t.updated_at = datetime.utcnow()
                s.add(t)
                s.commit()
                s.refresh(t)
                return t

        def delete(self, trade_id: int) -> None:
            with DBSession() as s:
                t = s.get(Trade, trade_id)
                if not t:
                    raise ValueError("trade_not_found")
                s.delete(t)
                s.commit()

trade_service = TradeService()
