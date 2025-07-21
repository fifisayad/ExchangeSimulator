import pytest

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
