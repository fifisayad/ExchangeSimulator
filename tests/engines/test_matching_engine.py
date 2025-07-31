import pytest

from src.common.exceptions import InvalidOrder
from src.engines.matching_engine import MatchingEngine
from src.enums.order_type import OrderType
from src.schemas.position_schema import PositionSchema
from src.services import PositionService, OrderService, BalanceService
from tests.materials import *


LOGGER = GetLogger().get()


@pytest.mark.asyncio
class TestMatchingEngine:
    position_service = PositionService()
    order_service = OrderService()
    balance_service = BalanceService()
    matching_engine = MatchingEngine()

    async def test_perpetual_open_position_check(self, database_provider_test):
        checked = await self.matching_engine.perpetual_open_position_check(
            market=Market.BTCUSD_PERP,
            portfolio_id="iamrich",
            side=OrderSide.SELL,
            size=0.123,
        )
        assert not checked

        position_schema = PositionSchema(
            portfolio_id="iamrich",
            market=Market.BTCUSD_PERP,
            side=PositionSide.LONG,
            status=PositionStatus.OPEN,
            size=0.1234,
        )
        position = await self.position_service.create(data=position_schema)

        checked = await self.matching_engine.perpetual_open_position_check(
            market=Market.BTCUSD_PERP,
            portfolio_id="iamrich",
            side=OrderSide.SELL,
            size=0.1234,
        )
        assert checked

        checked = await self.matching_engine.perpetual_open_position_check(
            market=Market.BTCUSD_PERP,
            portfolio_id="iamrich",
            side=OrderSide.SELL,
            size=0.123,
        )
        assert checked

        checked = await self.matching_engine.perpetual_open_position_check(
            market=Market.ETHUSD_PERP,
            portfolio_id="iamrich",
            side=OrderSide.SELL,
            size=0.123,
        )
        assert not checked

        checked = await self.matching_engine.perpetual_open_position_check(
            market=Market.BTCUSD_PERP,
            portfolio_id="iamrich",
            side=OrderSide.BUY,
            size=0.123,
        )
        assert not checked

        with pytest.raises(InvalidOrder):
            checked = await self.matching_engine.perpetual_open_position_check(
                market=Market.BTCUSD_PERP,
                portfolio_id="iamrich",
                side=OrderSide.SELL,
                size=0.134,
            )

    async def create_portfolio(self):
        await self.balance_service.create_by_qty(
            portfolio_id="iamrich", asset=Asset.BTC, qty=0.005
        )
        await self.balance_service.create_by_qty(
            portfolio_id="iamrich", asset=Asset.USD, qty=2000
        )

    async def test_fill_order_sucess_story(self, database_provider_test):
        await self.create_portfolio()
        await self.balance_service.lock_balance(
            portfolio_id="iamrich", asset=Asset.USD, locked_qty=300
        )
        order_schema = OrderSchema(
            portfolio_id="iamrich",
            market=Market.BTCUSD,
            price=1000,
            size=0.25,
            side=OrderSide.BUY,
            fee=0.00045,
            type=OrderType.LIMIT,
            status=OrderStatus.ACTIVE,
        )
        order = await self.order_service.create(data=order_schema)
        await self.matching_engine.fill_order(order)

        updated_order = await self.order_service.read_by_id(id_=order.id)
        assert updated_order is not None
        assert updated_order.status == OrderStatus.FILLED

        btc_balance = await self.balance_service.read_by_asset(
            portfolio_id="iamrich", asset=Asset.BTC
        )
        assert btc_balance is not None
        assert btc_balance.available == 0.005 + 0.25 - 0.00045

        usd_balance = await self.balance_service.read_by_asset(
            portfolio_id="iamrich", asset=Asset.USD
        )
        assert usd_balance is not None
        assert usd_balance.available == 1700

    async def test_fill_order_perpetual_story(self, database_provider_test):
        await self.create_portfolio()
        await self.balance_service.lock_balance(
            portfolio_id="iamrich", asset=Asset.USD, locked_qty=300
        )
        order_schema = OrderSchema(
            portfolio_id="iamrich",
            market=Market.BTCUSD_PERP,
            price=1000,
            size=0.25,
            side=OrderSide.BUY,
            fee=50,
            type=OrderType.LIMIT,
            status=OrderStatus.ACTIVE,
        )
        order = await self.order_service.create(data=order_schema)
        await self.matching_engine.fill_order(order)

        updated_order = await self.order_service.read_by_id(id_=order.id)
        assert updated_order is not None
        assert updated_order.status == OrderStatus.FILLED

        btc_balance = await self.balance_service.read_by_asset(
            portfolio_id="iamrich", asset=Asset.BTC
        )
        assert btc_balance is not None
        assert btc_balance.available == 0.005

        usd_balance = await self.balance_service.read_by_asset(
            portfolio_id="iamrich", asset=Asset.USD
        )
        assert usd_balance is not None
        assert usd_balance.available == 1650
        assert usd_balance.fee_paid == 50

    async def test_fill_order_or_filled(self, database_provider_test):
        await self.create_portfolio()
        order_schema = OrderSchema(
            portfolio_id="iamrich",
            market=Market.BTCUSD_PERP,
            price=1000,
            size=0.25,
            side=OrderSide.BUY,
            fee=50,
            type=OrderType.LIMIT,
            status=OrderStatus.CANCELED,
        )
        order = await self.order_service.create(data=order_schema)
        await self.matching_engine.fill_order(order)

        updated_order = await self.order_service.read_by_id(id_=order.id)
        assert updated_order is not None
        assert updated_order.status == OrderStatus.CANCELED

        btc_balance = await self.balance_service.read_by_asset(
            portfolio_id="iamrich", asset=Asset.BTC
        )
        assert btc_balance is not None
        assert btc_balance.available == 0.005

        usd_balance = await self.balance_service.read_by_asset(
            portfolio_id="iamrich", asset=Asset.USD
        )
        assert usd_balance is not None
        assert usd_balance.available == 2000
