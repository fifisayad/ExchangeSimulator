from typing import Tuple
from fifi import GetLogger
import pytest

from src.enums.asset import Asset
from src.enums.market import Market
from src.enums.order_side import OrderSide
from src.enums.order_status import OrderStatus
from src.enums.position_side import PositionSide
from src.enums.position_status import PositionStatus
from src.helpers.position_helpers import PositionHelpers
from src.models.leverage import Leverage
from src.models.order import Order
from src.models.position import Position
from src.schemas.order_schema import OrderSchema
from src.schemas.position_schema import PositionSchema
from src.services import *
from src.engines.positions_orchestration_engine import PositionsOrchestrationEngine

LOGGER = GetLogger().get()


@pytest.mark.asyncio
class TestPositionsOrchestrationEngine:
    position_service = PositionService()
    order_service = OrderService()
    balance_service = BalanceService()
    portfolio_service = PortfolioService()
    leverage_service = LeverageService()
    positions_orchestration_engine = PositionsOrchestrationEngine()

    async def create_fake_balances(self, portfolio_id: str = "iamrich"):
        await self.balance_service.create_by_qty(
            portfolio_id=portfolio_id, asset=Asset.USD, qty=2000
        )

    async def create_order_and_leverage(
        self, portfolio_id: str = "iamrich"
    ) -> Tuple[Leverage, Order]:
        await self.create_fake_balances()
        leverage = await self.leverage_service.create_or_update_leverage(
            portfolio_id=portfolio_id, market=Market.BTCUSD_PERP, leverage=2
        )
        assert leverage is not None
        order_schema = OrderSchema(
            portfolio_id=portfolio_id,
            market=Market.BTCUSD_PERP,
            price=1000,
            size=0.5,
            fee=0.1,
            side=OrderSide.BUY,
            status=OrderStatus.FILLED,
        )
        order = await self.order_service.create(data=order_schema)
        assert order is not None
        return leverage, order

    async def test_create_position_by_order(self, database_provider_test):
        leverage, order = await self.create_order_and_leverage()
        position = await self.positions_orchestration_engine.create_position_by_order(
            order
        )
        assert position.entry_price == order.price
        assert position.leverage == 2
        assert position.margin == 250
        assert position.side == PositionSide.LONG
        assert position.lqd_price == PositionHelpers.lqd_price_calc(
            entry_price=order.price, leverage=2, side=PositionSide.LONG
        )
        assert position.portfolio_id == "iamrich"
        assert position.size == order.size

        updated_order = await self.order_service.read_by_id(order.id)
        assert updated_order is not None
        assert updated_order.position_id == position.id

    async def test_liquid_position(
        self,
        database_provider_test,
    ):
        leverage, order = await self.create_order_and_leverage()
        assert await self.balance_service.lock_balance(
            portfolio_id="iamrich", asset=Asset.USD, locked_qty=300
        )
        position = await self.positions_orchestration_engine.create_position_by_order(
            order
        )
        await self.positions_orchestration_engine.liquid_position(position)

        updated_position = await self.position_service.read_by_id(position.id)
        assert updated_position is not None
        assert updated_position.status == PositionStatus.LIQUID
        assert updated_position.pnl == (-1) * position.margin

        updated_balance = await self.balance_service.read_by_asset(
            portfolio_id="iamrich", asset=Asset.USD
        )
        assert updated_balance is not None
        assert updated_balance.available == 1700
        assert updated_balance.quantity == 1750
        assert updated_balance.burned == 250
        assert updated_balance.frozen == 50

    async def test_close_position(
        self,
        database_provider_test,
    ):
        leverage, order = await self.create_order_and_leverage()
        assert await self.balance_service.lock_balance(
            portfolio_id="iamrich", asset=Asset.USD, locked_qty=300
        )
        position = await self.positions_orchestration_engine.create_position_by_order(
            order
        )

        order_schema = OrderSchema(
            portfolio_id="iamrich",
            market=Market.BTCUSD_PERP,
            price=1100,
            size=0.5,
            fee=0.1,
            side=OrderSide.SELL,
            status=OrderStatus.FILLED,
        )
        order = await self.order_service.create(data=order_schema)
        await self.positions_orchestration_engine.close_position(order, position)

        updated_position = await self.position_service.read_by_id(position.id)
        assert updated_position is not None
        assert updated_position.status == PositionStatus.CLOSE
        assert updated_position.pnl == 50
        assert updated_position.close_price == order.price

        updated_balance = await self.balance_service.read_by_asset(
            portfolio_id="iamrich", asset=Asset.USD
        )
        assert updated_balance is not None
        assert updated_balance.available == 2000
        assert updated_balance.quantity == 2050
        assert updated_balance.burned == 0
        assert updated_balance.frozen == 50

        updated_order = await self.order_service.read_by_id(order.id)
        assert updated_order is not None
        assert updated_order.position_id == position.id

    async def test_close_partially_position(
        self,
        database_provider_test,
    ):
        leverage, order = await self.create_order_and_leverage()
        assert await self.balance_service.lock_balance(
            portfolio_id="iamrich", asset=Asset.USD, locked_qty=300
        )
        position = await self.positions_orchestration_engine.create_position_by_order(
            order
        )

        order_schema = OrderSchema(
            portfolio_id="iamrich",
            market=Market.BTCUSD_PERP,
            price=1100,
            size=0.25,
            fee=0.1,
            side=OrderSide.SELL,
            status=OrderStatus.FILLED,
        )
        order = await self.order_service.create(data=order_schema)
        await self.positions_orchestration_engine.close_partially_position(
            order, position
        )

        updated_position = await self.position_service.read_by_id(position.id)
        assert updated_position is not None
        assert updated_position.status == PositionStatus.OPEN
        assert updated_position.pnl == 25
        assert updated_position.margin == 125
        assert updated_position.close_price == order.price

        updated_balance = await self.balance_service.read_by_asset(
            portfolio_id="iamrich", asset=Asset.USD
        )
        assert updated_balance is not None
        assert updated_balance.available == 1850
        assert updated_balance.quantity == 2025
        assert updated_balance.burned == 0
        assert updated_balance.frozen == 175

        updated_order = await self.order_service.read_by_id(order.id)
        assert updated_order is not None
        assert updated_order.position_id == position.id

    async def test_merge_position_with_order(
        self,
        database_provider_test,
    ):
        leverage, order = await self.create_order_and_leverage()
        assert await self.balance_service.lock_balance(
            portfolio_id="iamrich", asset=Asset.USD, locked_qty=300
        )
        position = await self.positions_orchestration_engine.create_position_by_order(
            order
        )

        order_schema = OrderSchema(
            portfolio_id="iamrich",
            market=Market.BTCUSD_PERP,
            price=1100,
            size=0.1,
            fee=0.1,
            side=OrderSide.BUY,
            status=OrderStatus.FILLED,
        )
        order = await self.order_service.create(data=order_schema)
        await self.positions_orchestration_engine.merge_order_with_position(
            order, position
        )

        updated_position = await self.position_service.read_by_id(position.id)
        assert updated_position is not None
        assert updated_position.status == PositionStatus.OPEN
        assert updated_position.pnl == 0
        entry_price = ((1000 * 0.5) + (1100 * 0.1)) / 0.6
        assert updated_position.entry_price == entry_price
        assert updated_position.lqd_price == entry_price - (
            entry_price / leverage.leverage
        )
        assert updated_position.margin == 305

        updated_balance = await self.balance_service.read_by_asset(
            portfolio_id="iamrich", asset=Asset.USD
        )
        assert updated_balance is not None
        assert updated_balance.available == 1700
        assert updated_balance.quantity == 2000
        assert updated_balance.burned == 0
        assert updated_balance.frozen == 300

        updated_order = await self.order_service.read_by_id(order.id)
        assert updated_order is not None
        assert updated_order.position_id == position.id
