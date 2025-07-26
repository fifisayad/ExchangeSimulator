from pydantic import BaseModel

from ..enums.market import Market
from ..enums.position_side import PositionSide
from ..enums.position_status import PositionStatus


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


class PositionReadSchema(BaseModel):
    id: str | None = None
    portfolio_id: str | None = None
    market: Market | None = None
    side: PositionSide | None = None
    status: PositionStatus | None = None


class PositionResponseSchema(BaseModel):
    id: str
    portfolio_id: str
    market: Market
    side: PositionSide
    status: PositionStatus
    entry_price: float
    lqd_price: float
    size: float
    leverage: float
    margin: float
