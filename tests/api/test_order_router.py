from fifi import GetLogger
import pytest
from unittest.mock import patch
from httpx import ASGITransport, AsyncClient
from main import app
from fastapi.encoders import jsonable_encoder

from src.common.exceptions import InvalidOrder
from src.services import OrderService
from src.engines.matching_engine import MatchingEngine
from src.schemas.order_schema import OrderResponseSchema
from tests.materials import *

LOGGER = GetLogger().get()


@pytest.mark.asyncio
class TestOrderRouter:
    order_service = OrderService()

    async def create_order(self, order_factory):
        order_schemas = order_factory()
        return await self.order_service.create_many(data=order_schemas)

    async def test_order_read_by_id(self, database_provider_test, order_factory):
        orders = await self.create_order(order_factory)
        order = orders[-1]
        with patch.object(
            OrderService, "read_by_id", return_value=order
        ) as mock_method:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test/exapi/v1"
            ) as ac:
                response = await ac.get(f"/order?order_id={order.id}")
                assert response.status_code == 200
                LOGGER.info(f"order response: {response.json()}")
                assert response.json() == jsonable_encoder(
                    OrderResponseSchema(**order.to_dict())
                )
                mock_method.assert_awaited_once_with(id_=order.id)

    async def test_order_read_by_id_failed(self, database_provider_test, order_factory):
        with patch.object(OrderService, "read_by_id", return_value=None) as mock_method:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test/exapi/v1"
            ) as ac:
                response = await ac.get(f"/order?order_id=SHIT")
                assert response.status_code == 404
                LOGGER.info(f"order response: {response.json()}")

                mock_method.assert_awaited_once_with(id_="SHIT")

    async def test_order_read_by_portfolio_id(
        self, database_provider_test, order_factory
    ):
        orders = await self.create_order(order_factory)
        order = orders[-1]
        with patch.object(
            OrderService, "read_orders_by_portfolio_id", return_value=orders
        ) as mock_method:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test/exapi/v1"
            ) as ac:
                response = await ac.get(f"/order?portfolio_id={order.portfolio_id}")
                assert response.status_code == 200
                LOGGER.info(f"order response: {response.json()}")
                expected_list = []
                for _order in orders:
                    expected_list.append(
                        jsonable_encoder(OrderResponseSchema(**_order.to_dict()))
                    )
                assert response.json() == expected_list
                mock_method.assert_awaited_once_with(
                    portfolio_id=order.portfolio_id,
                )

    async def test_order_read_by_filters(self, database_provider_test, order_factory):
        orders = await self.create_order(order_factory)
        order = orders[-1]
        with patch.object(
            OrderService, "read_orders_by_portfolio_id", return_value=order
        ) as mock_method:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test/exapi/v1"
            ) as ac:
                response = await ac.get(f"""/order?portfolio_id={order.portfolio_id}""")
                assert response.status_code == 200
                LOGGER.info(f"order response: {response.json()}")
                assert response.json() == jsonable_encoder(
                    OrderResponseSchema(**order.to_dict())
                )

                mock_method.assert_awaited_once_with(
                    portfolio_id=order.portfolio_id,
                )

    async def test_order_read_by_filters_failed(self, database_provider_test):
        with patch.object(
            OrderService, "read_orders_by_portfolio_id", return_value=[]
        ) as mock_method:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test/exapi/v1"
            ) as ac:
                response = await ac.get(f"""/order?portfolio_id=h1""")
                assert response.status_code == 404
                LOGGER.info(f"order response: {response.json()}")

                mock_method.assert_awaited_once_with(
                    portfolio_id="h1",
                )

    async def test_order_read_failed(self, database_provider_test):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test/exapi/v1"
        ) as ac:
            response = await ac.get(f"""/order""")
            assert response.status_code == 400
            LOGGER.info(f"order response: {response.json()}")

    async def test_cancel_order(self, database_provider_test, order_factory):
        orders = await self.create_order(order_factory)
        order = orders[-1]
        with patch.object(
            MatchingEngine(), "cancel_order", return_value=order
        ) as mock_method:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test/exapi/v1"
            ) as ac:
                response = await ac.patch(f"/order/cancel?order_id={order.id}")
                assert response.status_code == 200
                LOGGER.info(f"order response: {response.json()}")
                assert response.json() == jsonable_encoder(
                    OrderResponseSchema(**order.to_dict())
                )
                mock_method.assert_awaited_once_with(order_id=order.id)

    async def test_cancel_order_failed(self, database_provider_test):
        with patch.object(
            MatchingEngine, "cancel_order", side_effect=InvalidOrder
        ) as mock_method:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test/exapi/v1"
            ) as ac:
                response = await ac.patch(f"/order/cancel?order_id=sdfsfd")
                assert response.status_code == 400
                LOGGER.info(f"order response: {response.json()}")
