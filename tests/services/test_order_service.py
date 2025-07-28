import pytest

from src.models import Order
from src.services import OrderService
from tests.materials import *

LOGGER = GetLogger().get()


@pytest.mark.asyncio
class TestOrderService:
    order_service = OrderService()

    async def test_create_by_qty(self, database_provider_test, order_factory):
        order_schemas = order_factory(count=100)
        orders: List[Order] = await self.order_service.create_many(data=order_schemas)

        unique_open_order_ids = set()
        for order in orders:
            if order.status == OrderStatus.ACTIVE:
                unique_open_order_ids.add(order.id)
        LOGGER.info(f"{len(unique_open_order_ids)=}")

        open_orders = await self.order_service.get_open_orders()

        for order in open_orders:
            assert order.id in unique_open_order_ids
