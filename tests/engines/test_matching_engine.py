import pytest
import logging
from unittest.mock import patch

from src.common.exceptions import InvalidOrder, NotFoundOrder
from src.engines.matching_engine import MatchingEngine
from src.enums.order_type import OrderType
from src.models.order import Order
from src.models.portfolio import Portfolio
from src.schemas.position_schema import PositionSchema
from src.services import (
    PositionService,
    OrderService,
    BalanceService,
    PortfolioService,
    LeverageService,
)
from tests.materials import *


LOGGER = logging.getLogger(__name__)


@pytest.mark.asyncio
class TestMatchingEngine:
    position_service = PositionService()
    order_service = OrderService()
    balance_service = BalanceService()
    portfolio_service = PortfolioService()
    matching_engine = MatchingEngine()
    leverage_service = LeverageService()

    async def test_perpetual_open_position_check(
        self,
        database_provider_test,
    ):
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

    async def create_fake_balances(self, portfolio_id: str = "iamrich"):
        await self.balance_service.create_by_qty(
            portfolio_id=portfolio_id, asset=Asset.BTC, qty=0.05
        )
        await self.balance_service.create_by_qty(
            portfolio_id=portfolio_id, asset=Asset.USD, qty=2000
        )

    async def test_fill_order_sucess_story(
        self,
        database_provider_test,
    ):
        await self.create_fake_balances()
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
        assert btc_balance.available == 0.05 + 0.25 - 0.00045

        usd_balance = await self.balance_service.read_by_asset(
            portfolio_id="iamrich", asset=Asset.USD
        )
        assert usd_balance is not None
        assert usd_balance.available == 1700

    async def test_fill_order_perpetual_story(
        self,
        database_provider_test,
    ):
        await self.create_fake_balances()
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
        assert btc_balance.available == 0.05

        usd_balance = await self.balance_service.read_by_asset(
            portfolio_id="iamrich", asset=Asset.USD
        )
        assert usd_balance is not None
        assert usd_balance.available == 1650
        assert usd_balance.fee_paid == 50

    async def test_fill_order_or_filled(
        self,
        database_provider_test,
    ):
        await self.create_fake_balances()
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
        assert btc_balance.available == 0.05

        usd_balance = await self.balance_service.read_by_asset(
            portfolio_id="iamrich", asset=Asset.USD
        )
        assert usd_balance is not None
        assert usd_balance.available == 2000

    async def test_cancel_order_sucess_story(
        self,
        database_provider_test,
    ):
        await self.create_fake_balances()
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

        await self.matching_engine.cancel_order(order_id=order.id)

        updated_order = await self.order_service.read_by_id(id_=order.id)
        assert updated_order is not None
        assert updated_order.status == OrderStatus.CANCELED

        btc_balance = await self.balance_service.read_by_asset(
            portfolio_id="iamrich", asset=Asset.BTC
        )
        assert btc_balance is not None
        assert btc_balance.available == 0.05

        usd_balance = await self.balance_service.read_by_asset(
            portfolio_id="iamrich", asset=Asset.USD
        )
        assert usd_balance is not None
        assert usd_balance.available == 1950

    async def test_cancel_order_not_found(
        self,
        database_provider_test,
    ):
        with pytest.raises(NotFoundOrder):
            await self.matching_engine.cancel_order(order_id="iampoor")

    async def test_cancel_filled_order(
        self,
        database_provider_test,
    ):
        order_schema = OrderSchema(
            portfolio_id="iamrich",
            market=Market.BTCUSD_PERP,
            price=1000,
            size=0.25,
            side=OrderSide.BUY,
            fee=50,
            type=OrderType.LIMIT,
            status=OrderStatus.FILLED,
        )
        order = await self.order_service.create(data=order_schema)
        with pytest.raises(InvalidOrder):
            await self.matching_engine.cancel_order(order_id=order.id)

    async def test_cancel_canceled_order(
        self,
        database_provider_test,
    ):
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
        with pytest.raises(InvalidOrder):
            await self.matching_engine.cancel_order(order_id=order.id)

    async def test_create_order_wrong_portfolio_id(
        self,
        database_provider_test,
    ):
        with pytest.raises(InvalidOrder):
            await self.matching_engine.create_order(
                market=Market.BTCUSD,
                portfolio_id="ThisShitIsImpossible",
                price=1234324,
                size=342234,
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
            )

    async def create_fake_portfolio(self) -> Portfolio:
        return await self.portfolio_service.create(
            data=PortfolioSchema(name="CrazyTrader")
        )

    async def test_create_spot_market_order(
        self,
        database_provider_test,
    ):
        portfolio = await self.create_fake_portfolio()
        await self.create_fake_balances(portfolio_id=portfolio.id)
        order = await self.matching_engine.create_order(
            portfolio_id=portfolio.id,
            market=Market.BTCUSD,
            price=1100,
            size=0.25,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
        )

        assert order.price == 1100
        assert order.status == OrderStatus.FILLED
        assert order.fee != 0

        btc_balance = await self.balance_service.read_by_asset(
            portfolio_id=portfolio.id, asset=Asset.BTC
        )
        assert btc_balance is not None
        assert btc_balance.available == 0.05 + 0.25 - order.fee
        assert btc_balance.fee_paid == order.fee

        usd_balance = await self.balance_service.read_by_asset(
            portfolio_id=portfolio.id, asset=Asset.USD
        )
        assert usd_balance is not None
        assert usd_balance.available == 2000 - order.price * order.size

    async def test_create_perp_market_order(
        self,
        database_provider_test,
    ):
        portfolio = await self.create_fake_portfolio()
        leverage = await self.leverage_service.create_or_update_leverage(
            portfolio_id=portfolio.id, market=Market.BTCUSD_PERP, leverage=2
        )
        assert leverage is not None
        await self.create_fake_balances(portfolio_id=portfolio.id)
        order = await self.matching_engine.create_order(
            portfolio_id=portfolio.id,
            market=Market.BTCUSD_PERP,
            price=1100,
            size=0.25,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
        )

        assert order.price == 1100
        assert order.status == OrderStatus.FILLED
        assert order.fee != 0

        btc_balance = await self.balance_service.read_by_asset(
            portfolio_id=portfolio.id, asset=Asset.BTC
        )
        assert btc_balance is not None
        assert btc_balance.available == 0.05
        assert btc_balance.fee_paid == 0

        usd_balance = await self.balance_service.read_by_asset(
            portfolio_id=portfolio.id, asset=Asset.USD
        )
        assert usd_balance is not None
        assert (
            usd_balance.available
            == 2000 - (order.price * order.size / leverage.leverage) - order.fee
        )
        assert usd_balance.quantity == 2000 - order.fee
        assert usd_balance.frozen == (order.price * order.size / leverage.leverage)
        assert usd_balance.fee_paid == order.fee

    async def test_create_spot_limit_order(
        self,
        database_provider_test,
    ):
        with patch.object(
            self.matching_engine.mm_service, "get_last_trade", return_value=1100
        ) as mock_trade:
            portfolio = await self.create_fake_portfolio()
            await self.create_fake_balances(portfolio_id=portfolio.id)
            order = await self.matching_engine.create_order(
                portfolio_id=portfolio.id,
                market=Market.BTCUSD,
                price=1000,
                size=0.25,
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
            )
            mock_trade.assert_not_called()

        assert order.price == 1000
        assert order.status == OrderStatus.ACTIVE
        assert order.fee != 0

        btc_balance = await self.balance_service.read_by_asset(
            portfolio_id=portfolio.id, asset=Asset.BTC
        )
        assert btc_balance is not None
        assert btc_balance.available == 0.05
        assert btc_balance.fee_paid == 0

        usd_balance = await self.balance_service.read_by_asset(
            portfolio_id=portfolio.id, asset=Asset.USD
        )
        assert usd_balance is not None
        assert usd_balance.available == 2000 - order.price * order.size
        assert usd_balance.frozen == order.price * order.size

    async def test_create_perp_limit_order(
        self,
        database_provider_test,
    ):
        with patch.object(
            self.matching_engine.mm_service, "get_last_trade", return_value=1100
        ) as mock_trade:
            portfolio = await self.create_fake_portfolio()
            leverage = await self.leverage_service.create_or_update_leverage(
                portfolio_id=portfolio.id, market=Market.BTCUSD_PERP, leverage=3
            )
            assert leverage is not None
            await self.create_fake_balances(portfolio_id=portfolio.id)
            order = await self.matching_engine.create_order(
                portfolio_id=portfolio.id,
                market=Market.BTCUSD_PERP,
                price=1000,
                size=0.25,
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
            )
            mock_trade.assert_not_called()

        assert order.price == 1000
        assert order.status == OrderStatus.ACTIVE
        assert order.fee != 0

        btc_balance = await self.balance_service.read_by_asset(
            portfolio_id=portfolio.id, asset=Asset.BTC
        )
        assert btc_balance is not None
        assert btc_balance.available == 0.05
        assert btc_balance.fee_paid == 0

        usd_balance = await self.balance_service.read_by_asset(
            portfolio_id=portfolio.id, asset=Asset.USD
        )
        assert usd_balance is not None
        assert usd_balance.available == 2000 - (
            order.price * order.size / leverage.leverage
        )
        assert usd_balance.quantity == 2000
        assert usd_balance.frozen == (order.price * order.size / leverage.leverage)
        assert usd_balance.fee_paid == 0

    async def test_match_open_orders(
        self,
        database_provider_test,
    ):
        open_orders: List[Order] = list()
        portfolio = await self.create_fake_portfolio()
        await self.create_fake_balances(portfolio_id=portfolio.id)
        for price in [1000, 1200]:
            for side in [OrderSide.BUY, OrderSide.SELL]:
                open_orders.append(
                    await self.matching_engine.create_order(
                        portfolio_id=portfolio.id,
                        market=Market.BTCUSD,
                        price=price,
                        size=0.0025,
                        side=side,
                        order_type=OrderType.LIMIT,
                    )
                )
        with patch.object(
            self.matching_engine.mm_service,
            "get_last_trade",
            return_value={Market.BTCUSD: 1100},
        ) as mock_trade:
            await self.matching_engine.match_open_orders(open_orders=open_orders)
            assert mock_trade.call_count == 1

            open_orders = await self.order_service.get_open_orders()
            assert len(open_orders) == 2

            for order in open_orders:
                if order.side == OrderSide.BUY:
                    LOGGER.info(f"buy order={order.to_dict()}")
                    assert order.price == 1000
                if order.side == OrderSide.SELL:
                    LOGGER.info(f"sell order={order.to_dict()}")
                    assert order.price == 1200
