from pydantic import BaseModel

from fifi.enums import PositionSide, PositionStatus
from ..enums.market import Market


class PositionSchema(BaseModel):
    portfolio_id: str = ""
    market: Market = Market.BTCUSD_PERP
    side: PositionSide = PositionSide.LONG
    status: PositionStatus = PositionStatus.OPEN
    entry_price: float = 0
    lqd_price: float = 0
    size: float = 0
    leverage: float = 0
    margin: float = 0


class PositionResponseSchema(BaseModel):
    id: str
    portfolio_id: str
    market: Market
    side: PositionSide
    status: PositionStatus
    entry_price: float
    close_price: float
    lqd_price: float
    pnl: float
    size: float
    leverage: float
    margin: float
