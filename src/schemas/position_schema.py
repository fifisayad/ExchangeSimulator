from pydantic import BaseModel

from src.enums.market import Market
from src.enums.position_side import PositionSide


class PositionSchema(BaseModel):
    portfolio_id: str = ""
    market: Market = Market.BTCUSD_PERP
    side: PositionSide = PositionSide.LONG
    entry_price: float = 0
    lqd_price: float = 0
    size: float = 0
    leverage: float = 0
    margin: float = 0
