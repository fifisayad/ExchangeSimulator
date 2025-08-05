from fifi import GetLogger
import pytest
from unittest.mock import patch
from httpx import ASGITransport, AsyncClient
from main import app

from src.schemas.leverage_schema import LeverageSchema
from src.schemas.portfolio_schema import PortfolioResponseSchema, PortfolioSchema
from src.services import PortfolioService
from src.services.leverage_service import LeverageService
from tests.materials import *

LOGGER = GetLogger().get()


@pytest.mark.asyncio
class TestLeverageRouter:
    leverage_service = LeverageService()

    async def create_leverage(self, leverage_factory):
        leverage_schemas = leverage_factory()
        return await self.leverage_service.create_many(data=leverage_schemas)

    async def test_get_leverage_success(self, database_provider_test, leverage_factory):
        leverages = await self.create_leverage(leverage_factory)
        leverage = leverages[-1]
        with patch.object(
            LeverageService, "get_portfolio_market_leverage", return_value=leverage
        ) as mock_method:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test/exapi/v1"
            ) as ac:
                response = await ac.get(
                    f"/leverage?portfolio_id={leverage.portfolio_id}&market={leverage.market.value}"
                )
                assert response.status_code == 200
                LOGGER.info(f"leverage response: {response.json()}")
                mock_method.assert_awaited_once_with(
                    portfolio_id=leverage.portfolio_id, market=leverage.market
                )

    async def test_get_leverage_failed(self, database_provider_test):
        with patch.object(
            LeverageService, "get_portfolio_market_leverage", return_value=None
        ) as mock_method:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test/exapi/v1"
            ) as ac:
                response = await ac.get(f"/leverage?portfolio_id=dfsdff&market=btcusd")
                assert response.status_code == 404
                LOGGER.info(f"leverage response: {response.json()}")
                mock_method.assert_awaited_once_with(
                    portfolio_id="dfsdff", market=Market.BTCUSD
                )

    async def test_create_or_update_leverage(self, database_provider_test):
        with patch.object(
            LeverageService, "get_portfolio_market_leverage", return_value=None
        ) as mock_method:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test/exapi/v1"
            ) as ac:
                response = await ac.get(f"/leverage?portfolio_id=dfsdff&market=btcusd")
                assert response.status_code == 404
                LOGGER.info(f"leverage response: {response.json()}")
                mock_method.assert_awaited_once_with(
                    portfolio_id="dfsdff", market=Market.BTCUSD
                )
