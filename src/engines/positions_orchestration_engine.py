from typing import Dict
from fifi import MarketDataRepository, log_exception, singleton, BaseEngine
from fifi.helpers.get_current_time import GetCurrentTime
from fifi.enums import Asset, Market, PositionSide, PositionStatus
from fifi.helpers.get_logger import LoggerFactory

from ..helpers.position_helpers import PositionHelpers
from ..models.order import Order
from ..models.position import Position
from ..schemas.position_schema import PositionSchema
from ..services.leverage_service import LeverageService
from ..common.settings import Setting
from ..services import (
    OrderService,
    BalanceService,
    PositionService,
)


LOGGER = LoggerFactory().get(__name__)


@singleton
class PositionsOrchestrationEngine(BaseEngine):
    name: str = "positions_orchestration_engine"
    md_repos: Dict[Market, MarketDataRepository]

    def __init__(self):
        super().__init__(run_in_process=True)
        self.setting = Setting()
        self.order_service = OrderService()
        self.balance_service = BalanceService()
        self.position_service = PositionService()
        self.leverage_service = LeverageService()
        self.processed_orders = set()
        self.md_repos = dict()
        for market in self.setting.ACTIVE_MARKETS:
            self.md_repos[market] = MarketDataRepository(market, "1m")

    async def prepare(self):
        pass

    async def postpare(self):
        for market, repo in self.md_repos.items():
            repo.close()

    @log_exception()
    async def execute(self):
        LOGGER.info(f"{self.name} processing is started....")
        last_update = GetCurrentTime().get()
        while True:
            check_time = GetCurrentTime().get()
            filled_perp_orders = await self.order_service.get_filled_perp_orders(
                from_update_time=last_update
            )
            if len(filled_perp_orders) > 0:
                last_update = check_time
                LOGGER.info("new filled orders are arrived...")

            open_positions = await self.position_service.get_open_positions_hashmap()

            LOGGER.debug(f"{len(filled_perp_orders)=}, {len(open_positions)=}")
            for order in filled_perp_orders:
                if order.id not in self.processed_orders:
                    position_key = f"{order.market}_{order.portfolio_id}"
                    if position_key in open_positions:
                        await self.apply_order_to_position(
                            order=order, position=open_positions[position_key]
                        )
                    else:
                        await self.create_position_by_order(order=order)
                    self.processed_orders.add(order.id)

            for key, position in open_positions.items():
                market_last_trade = self.md_repos[position.market].get_last_trade()
                if position.side == PositionSide.LONG:
                    if position.lqd_price < market_last_trade:
                        continue

                if position.side == PositionSide.SHORT:
                    if position.lqd_price > market_last_trade:
                        continue

                await self.liquid_position(position=position)

    async def apply_order_to_position(self, order: Order, position: Position) -> None:
        """Applies an order to an existing position, either merging or closing it.

        Args:
            order (Order): The incoming order.
            position (Position): The existing position.
        """
        if PositionHelpers.is_order_against_position(order.side, position.side):
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
        await self.position_service.update_entity(position)
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
            entry_price=position.entry_price,
            close_price=order.price,
            size=order.size,
            side=position.side,
        )

        # unlock margin
        last_position_margin = position.margin
        position.closed_size += order.size
        position.margin = PositionHelpers.margin_calc(
            size=position.size - position.closed_size,
            leverage=position.leverage,
            price=position.entry_price,
        )
        LOGGER.debug(
            f"{position.id=} margin was {last_position_margin=} and it's now {position.margin=}"
        )
        is_unlocked = await self.balance_service.unlock_balance(
            portfolio_id=position.portfolio_id,
            asset=Asset.USD,
            unlocked_qty=last_position_margin - position.margin,
        )

        # add pnl value
        is_realized = await self.balance_service.add_balance(
            portfolio_id=position.portfolio_id, asset=Asset.USD, qty=position.pnl
        )
        if is_unlocked and is_realized:
            LOGGER.debug(
                f"closing partially position: {position.to_dict()} by order: {order.to_dict()}"
            )
            await self.position_service.update_entity(position)
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
            entry_price=position.entry_price,
            close_price=order.price,
            size=order.size,
            side=position.side,
        )
        position.status = PositionStatus.CLOSE
        position.closed_size = position.size

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
            await self.position_service.update_entity(position)
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
        leverage = await self.leverage_service.get_portfolio_market_leverage_value(
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
        position = await self.position_service.create(position_schema)
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
            await self.position_service.update_entity(position)
