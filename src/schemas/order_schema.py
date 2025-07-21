from pydantic import BaseModel

from ..enums.order_status import OrderStatus
from ..enums.order_side import OrderSide
from ..enums.order_type import OrderType


class OrderSchema(BaseModel):
    portfolio_id: str
    market: str
    fee: float
    price: float
    size: float
    leverage: int = 1
    status: OrderStatus = OrderStatus.ACTIVE
    side: OrderSide = OrderSide.BUY
    type: OrderType = OrderType.LIMIT
