import pytest

from src.models.order import Order
from src.repository import PortfolioRepository
from src.repository import BalanceRepository
from src.repository import OrderRepository
from tests.repository.materials import *


@pytest.mark.asyncio
class TestOrderRepository:
    portfilio_repo = PortfolioRepository()
    order_repo = OrderRepository()
    balance_repo = BalanceRepository()

    async def test_get_all_orders(self, database_provider_test, order_factory):
        order_schemas: List[OrderSchema] = order_factory()
        orders = await self.order_repo.create_many(
            data=order_schemas, return_models=True
        )
        orders_id_set = set()
        for order in orders:
            orders_id_set.add(order.id)

        got_orders = await self.order_repo.get_all_order()

        for order in got_orders:
            assert order.id in orders_id_set

    async def test_get_all_orders_with_status(
        self, database_provider_test, order_factory
    ):
        order_schemas: List[OrderSchema] = order_factory(count=100)
        orders = await self.order_repo.create_many(
            data=order_schemas, return_models=True
        )
        active_orders_id_set = set()
        for order in orders:
            if order.status == OrderStatus.ACTIVE:
                active_orders_id_set.add(order.id)

        LOGGER.info(
            f"[{self.__class__.__name__}]: active orders count: {len(active_orders_id_set)}"
        )
        got_orders = await self.order_repo.get_all_order(status=OrderStatus.ACTIVE)

        assert len(got_orders) == len(active_orders_id_set)

        for order in got_orders:
            assert order.id in active_orders_id_set

    async def test_get_filled_perp_orders(self, database_provider_test, order_factory):
        order_schemas: List[OrderSchema] = order_factory(count=1000)
        orders: List[Order] = await self.order_repo.create_many(
            data=order_schemas, return_models=True
        )
        filled_perp_orders_id_set = set()
        for order in orders:
            if order.status == OrderStatus.FILLED and order.market.is_perptual():
                filled_perp_orders_id_set.add(order.id)

        LOGGER.info(
            f"[{self.__class__.__name__}]: filled perp orders count: {len(filled_perp_orders_id_set)}"
        )
        got_orders = await self.order_repo.get_filled_perp_orders()

        assert len(got_orders) == len(filled_perp_orders_id_set)

        for order in got_orders:
            assert order.id in filled_perp_orders_id_set
