from fifi.helpers.get_current_time import GetCurrentTime
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
        assert len(open_orders) == len(unique_open_order_ids)
        for order in open_orders:
            assert order.id in unique_open_order_ids

    async def test_get_filled_perp_orders(self, database_provider_test, order_factory):
        order_schemas: List[OrderSchema] = order_factory(count=1000)
        orders: List[Order] = await self.order_service.create_many(data=order_schemas)
        filled_perp_orders_id_set = set()
        for order in orders:
            if order.status == OrderStatus.FILLED and order.market.is_perptual():
                filled_perp_orders_id_set.add(order.id)

        LOGGER.info(f"filled perp orders count: {len(filled_perp_orders_id_set)}")
        got_orders = await self.order_service.get_filled_perp_orders()

        assert len(got_orders) == len(filled_perp_orders_id_set)

        for order in got_orders:
            assert order.id in filled_perp_orders_id_set

    async def test_get_filled_perp_orders_with_update_from(
        self, database_provider_test, order_factory
    ):
        order_schemas: List[OrderSchema] = order_factory(count=1000)
        orders: List[Order] = await self.order_service.create_many(data=order_schemas)
        filled_perp_orders_id_set = set()
        update_time = GetCurrentTime().get()
        for order in orders:
            if order.status == OrderStatus.FILLED and order.market.is_perptual():
                if random.random() > 0.5:
                    filled_perp_orders_id_set.add(order.id)
                    order.price = random.random()
                    await self.order_service.update_entity(order)

        LOGGER.info(
            f"updated filled perp orders count: {len(filled_perp_orders_id_set)}"
        )
        got_orders = await self.order_service.get_filled_perp_orders(
            from_update_time=update_time
        )

        assert len(got_orders) == len(filled_perp_orders_id_set)

        for order in got_orders:
            assert order.id in filled_perp_orders_id_set
