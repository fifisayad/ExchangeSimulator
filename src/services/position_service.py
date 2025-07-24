from typing import Dict, List
from fifi import GetLogger

from ..enums.asset import Asset
from ..enums.position_status import PositionStatus
from ..models import Order, Position
from ..repository import PositionRepository
from ..schemas import PositionSchema
from ..helpers.position_helpers import PositionHelpers
from .service import Service
from .balance_service import BalanceService
from .order_service import OrderService
from .leverage_service import LeverageService


LOGGER = GetLogger().get()


class PositionService(Service):
    """Service class responsible for managing trading positions, including creation,
    merging, partial and full closure, and liquidation. It coordinates with repositories
    and other services to persist changes and manage balance updates."""

    def __init__(self) -> None:
        """Initializes the PositionService with repository and dependent services."""

        self._repo = PositionRepository()
        self.balance_service = BalanceService()
        self.order_service = OrderService()
        self.leverage_service = LeverageService()

    @property
    def repo(self) -> PositionRepository:
        return self._repo

    async def get_open_positions(self) -> List[Position]:
        """Fetches all currently open trading positions.

        Returns:
            List[Position]: A list of open positions.
        """
        return await self.repo.get_all_positions(status=PositionStatus.OPEN)

    async def get_open_positions_hashmap(self) -> Dict[str, Position]:
        """Returns a hashmap of open positions keyed by market and portfolio ID.

        Returns:
            Dict[str, Position]: A dictionary of open positions with keys in the format
            "{market}_{portfolio_id}".
        """
        open_positions = await self.get_open_positions()
        positions = dict()
        # unique hash for this is {market}_{portfolio_id}
        for position in open_positions:
            positions[f"{position.market}_{position.portfolio_id}"] = position
        return positions

    async def apply_order_to_position(self, order: Order, position: Position) -> None:
        """Applies an order to an existing position, either merging or closing it.

        Args:
            order (Order): The incoming order.
            position (Position): The existing position.
        """
        if PositionHelpers.is_order_against_position(order, position):
            if order.size >= position.size:
                await self.close_position(order, position)
            else:
                await self.close_partially_position(order, position)
        else:
            await self.merge_order_with_position(order, position)

    async def merge_order_with_position(self, order: Order, position: Position) -> None:
        """Merges an order into an existing position, updating price, size, and margin.

        Args:
            order (Order): The incoming order.
            position (Position): The position to update.
        """
        LOGGER.info(
            f"merging order with id: {order.id} into position with id: {position.id}"
        )
        position.entry_price = PositionHelpers.weighted_average_entry_price(
            position=position, order=order
        )
        position.lqd_price = PositionHelpers.lqd_price_calc(
            entry_price=position.entry_price,
            leverage=position.leverage,
            side=position.side,
        )
        position.size += order.size
        position.margin = PositionHelpers.margin_calc(
            size=position.size, leverage=position.leverage, price=position.entry_price
        )
        LOGGER.debug(
            f"order:{order.to_dict()} is merged with position: {position.to_dict()}"
        )
        await self.repo.update_entity(position)
        await self.order_service.set_position_id(order, position.id)

    async def close_partially_position(self, order: Order, position: Position) -> None:
        """Closes a position partially based on the order size.

        Args:
            order (Order): The closing order.
            position (Position): The position to update.
        """
        LOGGER.info(
            f"closing partially position with id: {position.id} by order with id: {order.id}"
        )
        position.close_price = order.price
        position.pnl += PositionHelpers.pnl_value(
            position=position,
            price=order.price,
            notional_value=order.price * order.size,
        )

        # unlock margin
        is_unlocked = await self.balance_service.unlock_balance(
            portfolio_id=position.portfolio_id,
            asset=Asset.USD,
            unlocked_qty=position.entry_price * order.size,
        )
        position.margin -= position.entry_price * order.size
        position.size -= order.size

        # add pnl value
        is_realized = await self.balance_service.add_balance(
            portfolio_id=position.portfolio_id, asset=Asset.USD, qty=position.pnl
        )
        if is_unlocked and is_realized:
            LOGGER.debug(
                f"closing partially position: {position.to_dict()} by order: {order.to_dict()}"
            )
            await self.repo.update_entity(position)
            await self.order_service.set_position_id(order, position.id)

    async def close_position(self, order: Order, position: Position) -> None:
        """Fully closes a position based on the order.

        Args:
            order (Order): The closing order.
            position (Position): The position to close.
        """
        LOGGER.info(
            f"closing position with id: {position.id} by order with id: {order.id}"
        )
        position.close_price = order.price
        position.pnl += PositionHelpers.pnl_value(
            position=position,
            price=order.price,
            notional_value=order.price * order.size,
        )
        position.status = PositionStatus.CLOSE

        # unlock margin
        is_unlocked = await self.balance_service.unlock_balance(
            portfolio_id=position.portfolio_id,
            asset=Asset.USD,
            unlocked_qty=position.margin,
        )

        # add pnl value
        is_realized = await self.balance_service.add_balance(
            portfolio_id=position.portfolio_id, asset=Asset.USD, qty=position.pnl
        )
        if is_unlocked & is_realized:
            LOGGER.debug(
                f"closing partially position: {position.to_dict()} by order: {order.to_dict()}"
            )
            await self.repo.update_entity(position)
            await self.order_service.set_position_id(order, position.id)

    async def create_position_by_order(self, order: Order) -> Position:
        """Creates a new trading position from a given order.

        Args:
            order (Order): The initiating order.

        Returns:
            Position: The newly created position.
        """
        LOGGER.info(f"creating new position by order with id: {order.id}")
        position_schema = PositionSchema()
        position_schema.entry_price = order.price
        position_schema.portfolio_id = order.portfolio_id
        position_schema.market = order.market
        position_schema.size = order.size
        position_schema.side = PositionHelpers.get_position_side_with_order(order)
        leverage = await self.leverage_service.get_portfolio_market_leverage(
            portfolio_id=position_schema.portfolio_id,
            market=order.market,
        )
        position_schema.leverage = leverage or 1
        position_schema.lqd_price = PositionHelpers.lqd_price_calc(
            entry_price=order.price,
            leverage=position_schema.leverage,
            side=position_schema.side,
        )
        position_schema.margin = PositionHelpers.margin_calc(
            position_schema.size, position_schema.leverage, position_schema.entry_price
        )
        position = await self.repo.create(position_schema)
        LOGGER.info(
            f"created new position by id:{position.id} by order with id: {order.id}"
        )
        LOGGER.debug(
            f"created new position:{position.to_dict()} by order:{order.to_dict()}"
        )
        await self.order_service.set_position_id(order, position.id)
        return position

    async def liquid_position(self, position: Position) -> None:
        """Liquidates a position due to margin requirements and updates balance accordingly.

        Args:
            position (Position): The position to liquidate.
        """
        LOGGER.info(f"liquiding a position by id:{position.id}")
        is_sucessful = await self.balance_service.burn_balance(
            portfolio_id=position.portfolio_id,
            asset=Asset.USD,
            burned_qty=position.margin,
        )
        if is_sucessful:
            position.pnl = (-1) * position.margin
            position.status = PositionStatus.LIQUID
            await self.repo.update_entity(position)
