from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Trade(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str
    side: str  # 'buy' | 'sell'
    quantity: float
    price: float
    status: str = "open"  # 'open' | 'executed' | 'canceled'
    note: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
