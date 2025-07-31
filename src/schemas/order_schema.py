from pydantic import BaseModel

from ..enums.order_status import OrderStatus
from ..enums.order_side import OrderSide
from ..enums.order_type import OrderType
from ..enums.market import Market


class OrderSchema(BaseModel):
    portfolio_id: str
    market: Market
    fee: float
    price: float
    size: float
    status: OrderStatus = OrderStatus.ACTIVE
    side: OrderSide = OrderSide.BUY
    type: OrderType = OrderType.LIMIT


class OrderCreateSchema(BaseModel):
    portfolio_id: str
    market: Market
    price: float
    size: float
    side: OrderSide
    type: OrderType


class OrderResponseSchema(BaseModel):
    id: str
    portfolio_id: str
    market: Market
    fee: float
    price: float
    size: float
    status: OrderStatus
    side: OrderSide
    type: OrderType
    position_id: str
