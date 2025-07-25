from datetime import datetime
from typing import List, Optional, Union

from ..helpers.order_helper import OrderHelper
from ..helpers.position_helpers import PositionHelpers
from ..common.exceptions import InvalidOrder, NotEnoughBalance
from ..enums.market import Market
from ..enums.order_side import OrderSide
from ..enums.order_type import OrderType
from ..enums.asset import Asset
from .service import Service
from ..enums.order_status import OrderStatus
from ..repository import OrderRepository
from ..models import Order
from ..schemas import OrderSchema
from .position_service import PositionService
from .balance_service import BalanceService
from .portfolio_service import PortfolioService


# TODO: REFACTOR get orders with filter and make it flexible
class OrderService(Service):
    """Service class responsible for managing and processing orders,
    including retrieving active/filled orders, calculating fees, and
    associating orders with positions."""

    def __init__(self):
        """Initializes the OrderService with its order repository."""
        self._repo = OrderRepository()
        self.position_service = PositionService()
        self.balance_service = BalanceService()
        self.portfolio_service = PortfolioService()

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

    async def check_lock_balance(
        self, portfolio_id: str, asset: Asset, qty: float, fee: float
    ) -> bool:
        is_locked = await self.balance_service.lock_balance(
            portfolio_id=portfolio_id, asset=asset, locked_qty=qty
        )
        is_paid = await self.balance_service.pay_fee(
            portfolio_id=portfolio_id, asset=asset, paid_qty=fee
        )
        if is_locked and is_paid:
            return True
        return False

    async def check_lock_balance_for_spot_limit_order_creation(
        self,
        portfolio_id: str,
        market: Market,
        size: float,
        side: OrderSide,
        fee: float,
    ) -> bool:
        return False

    async def check_lock_balance_for_perp_limit_order_creation(
        self,
        portfolio_id: str,
        market: Market,
        price: float,
        size: float,
        side: OrderSide,
        fee: float,
    ) -> bool:
        open_position = await self.position_service.get_by_portfolio_and_market(
            portfolio_id=portfolio_id, market=market
        )
        payment_asset = OrderHelper().get_payment_asset(market=market, side=side)
        order_total = price * size
        if open_position:
            # there is an active position
            if PositionHelpers().is_order_against_position(
                order_side=side, position_side=open_position.side
            ):
                # order against position
                if open_position.size >= size:
                    return True
                else:
                    raise InvalidOrder(
                        f"""there is an active position for {portfolio_id=}
                        with {open_position.size=}
                        order size must be equal or lessen than position size
                        """
                    )
        # order and position are same direction + there isn't active position
        if self.balance_service.check_available_qty(
            portfolio_id=portfolio_id,
            asset=payment_asset,
            qty=order_total + fee,
        ):
            return await self.check_lock_balance(
                portfolio_id=portfolio_id,
                asset=payment_asset,
                qty=order_total,
                fee=fee,
            )
        return False

    async def create_limit_order(
        self,
        portfolio_id: str,
        market: Market,
        price: float,
        size: float,
        side: OrderSide,
    ) -> Optional[Order]:
        order = None
        is_ok = False

        portfolio = await self.portfolio_service.read_by_id(id=portfolio_id)
        if not portfolio:
            raise InvalidOrder(f"{portfolio_id=} is invalid")

        order_fee = OrderHelper.fee_calc(
            market=market,
            price=price,
            size=size,
            side=side,
            order_type=OrderType.LIMIT,
            portfolio=portfolio,
        )
        if market.is_perptual():
            is_ok = await self.check_lock_balance_for_perp_limit_order_creation(
                portfolio_id=portfolio_id,
                market=market,
                price=price,
                size=size,
                side=side,
                fee=order_fee,
            )
        else:
            is_ok = await self.check_lock_balance_for_spot_limit_order_creation(
                portfolio_id=portfolio_id,
                market=market,
                size=size,
                side=side,
                fee=order_fee,
            )
        if not is_ok:
            raise NotEnoughBalance(
                f"""{side=} order for 
            {portfolio_id=} on {market=} 
            with {size=} can not be created"""
            )
        order_schema = OrderSchema(
            portfolio_id=portfolio_id,
            market=market,
            price=price,
            fee=order_fee,
            size=size,
            side=side,
            type=OrderType.LIMIT,
        )
        order = await self.create(data=order_schema)
        return order
