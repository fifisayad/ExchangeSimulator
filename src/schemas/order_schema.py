from pydantic import BaseModel

from ..enums.order_status import OrderStatus


class OrderSchema(BaseModel):
    portfolio_id: str
    market: str
    commission: float
    price: float
    stop_loss: float
    quantity: float
    leverage: int
    status: OrderStatus
