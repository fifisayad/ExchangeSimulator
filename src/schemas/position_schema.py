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
