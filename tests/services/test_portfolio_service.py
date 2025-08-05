import logging
import pytest

from src.services import PortfolioService
from tests.materials import *


LOGGER = logging.getLogger(__name__)


@pytest.mark.asyncio
class TestPortfolioService:
    portfilio_service = PortfolioService()

    async def test_read_by_name(self, database_provider_test, portfolio_factory):
        portfolios_schema = [portfolio_factory() for i in range(5)]
        portfolios = await self.portfilio_service.create_many(data=portfolios_schema)

        third_portfolio = await self.portfilio_service.read_by_name(
            name=portfolios[3].name
        )
        assert third_portfolio is not None
        assert third_portfolio.id == portfolios[3].id

    async def test_update_by_name(self, database_provider_test, portfolio_factory):
        portfolio_schema: PortfolioSchema = portfolio_factory()
        created_portfolio = await self.portfilio_service.create(data=portfolio_schema)
        assert created_portfolio is not None

        portfolio_schema.perp_maker_fee = 0.999
        updated_portfolio = await self.portfilio_service.update_by_name(
            name=portfolio_schema.name, data=portfolio_schema
        )

        assert updated_portfolio.id == created_portfolio.id
        got_portfolio = await self.portfilio_service.read_by_name(
            name=portfolio_schema.name
        )
        LOGGER.info(f"{created_portfolio.to_dict()=}")
        LOGGER.info(f"{updated_portfolio.to_dict()=}")

        assert got_portfolio is not None
        LOGGER.info(f"{got_portfolio.to_dict()=}")
        assert got_portfolio.perp_maker_fee == updated_portfolio.perp_maker_fee
