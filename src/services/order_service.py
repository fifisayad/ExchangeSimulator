from datetime import datetime
from typing import List, Optional

from .service import Service
from ..enums.order_status import OrderStatus
from ..repository import OrderRepository
from ..models import Order


# TODO: REFACTOR get orders with filter and make it flexible
class OrderService(Service):
    """Service class responsible for managing and processing orders,
    including retrieving active/filled orders, calculating fees, and
    associating orders with positions."""

    def __init__(self):
        """Initializes the OrderService with its order repository."""
        self._repo = OrderRepository()

    @property
    def repo(self) -> OrderRepository:
        return self._repo

    async def get_open_orders(self) -> List[Order]:
        """Retrieves all currently active (open) orders.

        Returns:
            List[Order]: A list of active orders.
        """
        return await self.repo.get_all_order(status=OrderStatus.ACTIVE)

    async def get_filled_perp_orders(
        self, from_update_time: Optional[datetime] = None
    ) -> List[Order]:
        """Fetches all filled perpetual orders, optionally filtering by update time.

        Args:
            from_update_time (Optional[datetime]): Only return orders updated after this timestamp.

        Returns:
            List[Order]: A list of filled perpetual orders.
        """
        return await self.repo.get_filled_perp_orders(from_update_time=from_update_time)

    async def set_position_id(self, order: Order, position_id: str) -> None:
        """Associates a given order with a trading position.

        Args:
            order (Order): The order to associate.
            position_id (str): The ID of the associated position.
        """
        order.position_id = position_id
        await self.repo.update_entity(order)

    async def read_orders_by_portfolio_id(self, portfolio_id: str) -> List[Order]:
        return await self.repo.get_entities_by_portfolio_id(portfolio_id=portfolio_id)
