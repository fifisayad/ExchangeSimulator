import pytest
import logging

from src.models import Leverage
from src.services import LeverageService
from tests.materials import *


LOGGER = logging.getLogger(__name__)


@pytest.mark.asyncio
class TestLeverageService:
    leverage_service = LeverageService()

    async def test_get_portfolio_market_leverage(
        self, database_provider_test, leverage_factory
    ):
        leverages_schemas = leverage_factory()
        leverages = await self.leverage_service.create_many(leverages_schemas)

        for leverage in leverages:
            got_leverage = await self.leverage_service.get_portfolio_market_leverage(
                portfolio_id=leverage.portfolio_id, market=leverage.market
            )

            assert got_leverage is not None
            assert got_leverage.leverage == leverage.leverage

    async def test_get_portfolio_market_leverage_value(
        self, database_provider_test, leverage_factory
    ):
        leverages_schemas = leverage_factory()
        leverages = await self.leverage_service.create_many(leverages_schemas)

        for leverage in leverages:
            got_leverage = (
                await self.leverage_service.get_portfolio_market_leverage_value(
                    portfolio_id=leverage.portfolio_id, market=leverage.market
                )
            )

            assert got_leverage is not None
            assert got_leverage == leverage.leverage

    async def test_create_leverage(self, database_provider_test, leverage_factory):
        leverages_schemas: List[LeverageSchema] = leverage_factory()
        leverages: List[Leverage] = list()
        for leverage_schema in leverages_schemas:
            leverage = await self.leverage_service.create_or_update_leverage(
                portfolio_id=leverage_schema.portfolio_id,
                market=leverage_schema.market,
                leverage=leverage_schema.leverage,
            )
            assert leverage is not None
            leverages.append(leverage)

        for leverage in leverages:
            got_leverage = await self.leverage_service.read_by_id(id_=leverage.id)

            assert got_leverage is not None
            assert got_leverage.leverage == leverage.leverage
            assert got_leverage.portfolio_id == leverage.portfolio_id
            assert got_leverage.market == leverage.market

    async def test_update_leverage(self, database_provider_test, leverage_factory):
        leverages_schemas: List[LeverageSchema] = leverage_factory()
        leverage_hash_map = dict()

        for leverage_schema in leverages_schemas:
            leverage_hash_map[
                f"{leverage_schema.portfolio_id}_{leverage_schema.market.value}"
            ] = leverage_schema.leverage
        leverages: List[Leverage] = await self.leverage_service.create_many(
            data=leverages_schemas
        )
        for leverage in leverages:
            got_leverage = await self.leverage_service.create_or_update_leverage(
                portfolio_id=leverage.portfolio_id,
                market=leverage.market,
                leverage=leverage.leverage + 1,
            )
            assert got_leverage is not None
            assert (
                got_leverage.leverage
                == leverage_hash_map[
                    f"{got_leverage.portfolio_id}_{got_leverage.market.value}"
                ]
                + 1
            )
