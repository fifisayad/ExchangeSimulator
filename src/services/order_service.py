from datetime import datetime
from typing import List, Optional, Union

from ..helpers.position_helpers import PositionHelpers
from ..common.exceptions import NotEnoughBalance
from ..enums.market import Market
from ..enums.order_side import OrderSide
from ..enums.order_type import OrderType
from .service import Service
from ..enums.order_status import OrderStatus
from ..repository import OrderRepository
from ..models import Order
from ..schemas import OrderSchema
from .position_service import PositionService


# TODO: REFACTOR get orders with filter and make it flexible
class OrderService(Service):
    """Service class responsible for managing and processing orders,
    including retrieving active/filled orders, calculating fees, and
    associating orders with positions."""

    def __init__(self):
        """Initializes the OrderService with its order repository."""
        self._repo = OrderRepository()
        self.position_service = PositionService()

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

    async def check_lock_balance_for_spot_order(
        self,
        portfolio_id: str,
        market: Market,
        price: float,
        size: float,
        side: OrderSide,
        order_type: OrderType,
    ) -> bool:
        return False

    async def check_lock_balance_for_perp_order(
        self,
        portfolio_id: str,
        market: Market,
        price: float,
        size: float,
        side: OrderSide,
        order_type: OrderType,
    ) -> bool:
        open_position = await self.position_service.get_by_portfolio_and_market(
            portfolio_id=portfolio_id, market=market
        )
        if open_position:
            # there is an active position
            if PositionHelpers().is_order_against_position(
                order_side=side, position_side=open_position.side
            ):
                # order against position
                pass
            else:
                # order and position are same direction
                pass
        else:
            # there isn't active postion
            pass

        return False

    async def create_order(
        self,
        portfolio_id: str,
        market: Market,
        price: float,
        size: float,
        order_type: OrderType,
        side: OrderSide,
    ) -> Optional[Order]:
        order = None
        is_ok = False
        if market.is_perptual():
            is_ok = await self.check_lock_balance_for_perp_order(
                portfolio_id=portfolio_id,
                market=market,
                price=price,
                size=size,
                order_type=order_type,
                side=side,
            )
        else:
            is_ok = await self.check_lock_balance_for_spot_order(
                portfolio_id=portfolio_id,
                market=market,
                price=price,
                size=size,
                order_type=order_type,
                side=side,
            )
        if not is_ok:
            raise NotEnoughBalance("")
        order_fee = await self.fee_calc(order)
        order_schema = OrderSchema(
            portfolio_id=portfolio_id,
            market=market,
            price=price,
            fee=order_fee,
            size=size,
            side=side,
            type=order_type,
        )
        order = await self.create(data=order_schema)
        return order
