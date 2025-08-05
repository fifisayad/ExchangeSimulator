from fifi import GetLogger
import pytest
from unittest.mock import patch, Mock
from httpx import ASGITransport, AsyncClient
from main import app
from fastapi.encoders import jsonable_encoder

from src.enums.data_type import DataType
from src.enums.exchange import Exchange
from src.enums.market import Market
from src.schemas.portfolio_schema import PortfolioResponseSchema, PortfolioSchema
from src.services import PortfolioService

LOGGER = GetLogger().get()


@pytest.mark.asyncio
class TestPortfolioRouter:
    portfolio_service = PortfolioService()

    async def create_portfolio(self, portfolio_name: str = "iamrich"):
        portfolio_schema = PortfolioSchema(name=portfolio_name)
        return await self.portfolio_service.create(data=portfolio_schema)

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
