from fifi import GetLogger
import pytest
import logging
from unittest.mock import patch
from httpx import ASGITransport, AsyncClient
from main import app

from src.schemas.portfolio_schema import PortfolioResponseSchema, PortfolioSchema
from src.services import PortfolioService


LOGGER = logging.getLogger(__name__)


@pytest.mark.asyncio
class TestPortfolioRouter:
    portfolio_service = PortfolioService()

    async def create_portfolio(self, portfolio_name: str = "iamrich"):
        portfolio_schema = PortfolioSchema(name=portfolio_name)
        return await self.portfolio_service.create(data=portfolio_schema)

    async def test_get_portfolio_success_by_name(self, database_provider_test):
        portfolio = await self.create_portfolio()
        with patch.object(
            PortfolioService, "read_by_name", return_value=portfolio
        ) as mock_method:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test/exapi/v1"
            ) as ac:
                response = await ac.get(f"/portfolio?name={portfolio.name}")
                assert response.status_code == 200
                LOGGER.info(f"portfolio response: {response.json()}")

                assert (
                    response.json()
                    == PortfolioResponseSchema(**portfolio.to_dict()).model_dump()
                )
                mock_method.assert_awaited_once_with(name=portfolio.name)

    async def test_get_portfolio_success_by_id(self, database_provider_test):
        portfolio = await self.create_portfolio()
        with patch.object(
            PortfolioService, "read_by_id", return_value=portfolio
        ) as mock_method:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test/exapi/v1"
            ) as ac:
                response = await ac.get(f"/portfolio?id={portfolio.id}")
                assert response.status_code == 200
                LOGGER.info(f"portfolio response: {response.json()}")

                assert (
                    response.json()
                    == PortfolioResponseSchema(**portfolio.to_dict()).model_dump()
                )
                mock_method.assert_awaited_once_with(id_=portfolio.id)

    async def test_get_portfolio_failed(self, database_provider_test):
        portfolio = await self.create_portfolio()
        with patch.object(
            PortfolioService, "read_by_id", return_value=None
        ) as mock_method:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test/exapi/v1"
            ) as ac:
                response = await ac.get(f"/portfolio?id={portfolio.id}")
                assert response.status_code == 404
                mock_method.assert_awaited_once_with(id_=portfolio.id)
        with patch.object(
            PortfolioService, "read_by_name", return_value=None
        ) as mock_method:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test/exapi/v1"
            ) as ac:
                response = await ac.get(f"/portfolio?name={portfolio.name}")
                assert response.status_code == 404
                mock_method.assert_awaited_once_with(name=portfolio.name)
        with patch.object(
            PortfolioService, "read_by_id", return_value=None
        ) as mock_method_id:
            with patch.object(
                PortfolioService, "read_by_name", return_value=None
            ) as mock_method_name:
                async with AsyncClient(
                    transport=ASGITransport(app=app), base_url="http://test/exapi/v1"
                ) as ac:
                    response = await ac.get(f"/portfolio")
                    assert response.status_code == 404
                    mock_method_id.assert_not_awaited()
                    mock_method_name.assert_not_awaited()

    async def test_create_portfolio_existed(self, database_provider_test):
        portfolio = await self.create_portfolio()
        portfolio_schema = PortfolioSchema(name=portfolio.name)
        with patch.object(
            PortfolioService, "read_by_name", return_value=portfolio
        ) as mock_method:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test/exapi/v1"
            ) as ac:
                response = await ac.post(
                    f"/portfolio", json=portfolio_schema.model_dump()
                )
                LOGGER.info(response.json())
                assert response.status_code == 400
                mock_method.assert_awaited_once_with(portfolio.name)

    async def test_create_portfolio(self, database_provider_test):
        portfolio = await self.create_portfolio()
        portfolio_schema = PortfolioSchema(name=portfolio.name, perp_maker_fee=0.0025)
        with patch.object(
            PortfolioService, "read_by_name", return_value=None
        ) as mock_method_read:
            with patch.object(
                PortfolioService, "create", return_value=portfolio
            ) as mock_method_create:
                async with AsyncClient(
                    transport=ASGITransport(app=app), base_url="http://test/exapi/v1"
                ) as ac:
                    response = await ac.post(
                        f"/portfolio", json=portfolio_schema.model_dump()
                    )
                    LOGGER.info(response.json())
                    assert response.status_code == 200
                    assert (
                        response.json()
                        == PortfolioResponseSchema(**portfolio.to_dict()).model_dump()
                    )
                    mock_method_read.assert_awaited_once_with(portfolio.name)
                    mock_method_create.assert_awaited_once_with(data=portfolio_schema)

    async def test_create_portfolio_exception(self, database_provider_test):
        portfolio = await self.create_portfolio()
        portfolio_schema = PortfolioSchema(name=portfolio.name, perp_maker_fee=0.0025)
        with patch.object(
            PortfolioService, "read_by_name", return_value=None
        ) as mock_method_read:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test/exapi/v1"
            ) as ac:
                response = await ac.post(
                    f"/portfolio", json=portfolio_schema.model_dump()
                )
                LOGGER.info(response.json())
                assert response.status_code == 400
                mock_method_read.assert_awaited_once_with(portfolio.name)

    async def test_update_portfolio_exception(self, database_provider_test):
        portfolio = await self.create_portfolio()
        portfolio_schema = PortfolioSchema(name=portfolio.name, perp_maker_fee=0.0025)
        with patch.object(
            PortfolioService, "update_by_name", return_value=portfolio
        ) as mock_method_read:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test/exapi/v1"
            ) as ac:
                response = await ac.patch(
                    f"/portfolio", json=portfolio_schema.model_dump()
                )
                LOGGER.info(response.json())
                assert response.status_code == 200
                assert (
                    response.json()
                    == PortfolioResponseSchema(**portfolio.to_dict()).model_dump()
                )
                mock_method_read.assert_awaited_once_with(
                    name=portfolio.name, data=portfolio_schema
                )
