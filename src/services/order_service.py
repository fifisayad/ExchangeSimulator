from typing import List

from ..enums.order_status import OrderStatus
from ..repository import OrderRepository
from ..models import Order


class OrderService:
    def __init__(self):
        self.order_repo = OrderRepository()

    async def get_open_orders(self) -> List[Order]:
        return await self.order_repo.get_all_order(status=OrderStatus.ACTIVE)
