from datetime import datetime
from typing import List, Optional, Union

from src.enums.order_side import OrderSide
from src.enums.order_type import OrderType

from ..enums.order_status import OrderStatus
from ..repository import OrderRepository
from ..models import Order


class OrderService:
    """Service class responsible for managing and processing orders,
    including retrieving active/filled orders, calculating fees, and
    associating orders with positions."""

    def __init__(self):
        """Initializes the OrderService with its order repository."""
        self.order_repo = OrderRepository()

    async def get_open_orders(self) -> List[Order]:
        """Retrieves all currently active (open) orders.

        Returns:
            List[Order]: A list of active orders.
        """
        return await self.order_repo.get_all_order(status=OrderStatus.ACTIVE)

    async def get_filled_perp_orders(
        self, from_update_time: Optional[datetime] = None
    ) -> List[Order]:
        """Fetches all filled perpetual orders, optionally filtering by update time.

        Args:
            from_update_time (Optional[datetime]): Only return orders updated after this timestamp.

        Returns:
            List[Order]: A list of filled perpetual orders.
        """
        return await self.order_repo.get_filled_perp_orders(
            from_update_time=from_update_time
        )

    async def set_position_id(self, order: Order, position_id: str) -> None:
        """Associates a given order with a trading position.

        Args:
            order (Order): The order to associate.
            position_id (str): The ID of the associated position.
        """
        order.position_id = position_id
        await self.order_repo.update_entity(order)

    async def fee_calc(self, orders: Union[Order, List[Order]]) -> None:
        """Calculates and applies trading fees to one or more orders based on
        order type, side, and whether the market is perpetual or spot.

        Args:
            orders (Union[Order, List[Order]]): A single order or a list of orders to calculate fees for.
        """
        orders_list = [orders] if isinstance(orders, Order) else orders
        for order in orders_list:
            order_total = order.size * order.price
            if order.market.is_perptual():
                if order.type == OrderType.LIMIT:
                    order.fee = order.portfolio.perp_maker_fee * order_total
                elif order.type == OrderType.MARKET:
                    order.fee = order.portfolio.perp_taker_fee * order_total
            else:
                if order.type == OrderType.LIMIT:
                    if order.side == OrderSide.BUY:
                        order.fee = order.size * order.portfolio.spot_maker_fee
                    else:
                        order.fee = order_total * order.portfolio.spot_maker_fee
                elif order.type == OrderType.MARKET:
                    if order.side == OrderSide.BUY:
                        order.fee = order.size * order.portfolio.spot_taker_fee
                    else:
                        order.fee = order_total * order.portfolio.spot_taker_fee
            await self.order_repo.update_entity(entity=order)
