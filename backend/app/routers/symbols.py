from fastapi import APIRouter
from ..services.market_data import CANDIDATES

router = APIRouter(prefix="/symbols", tags=["symbols"])

@router.get("")
def list_symbols():
    # logical symbols + provider candidates
    return {
        "supported": sorted(CANDIDATES.keys()),
        "mapping": {sym: [c[0] for c in candidates] for sym, candidates in CANDIDATES.items()},
    }
