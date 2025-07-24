from fifi.exceptions import IntegrityConflictException
import pytest

from src.repository import LeverageRepository
from src.enums.market import Market
from tests.materials import *


@pytest.mark.asyncio
class TestLeverageRepository:
    leverage_repository = LeverageRepository()

    async def test_get_all_leverages(self, database_provider_test, leverage_factory):
        leverage_schemas = leverage_factory()
        leverages = await self.leverage_repository.create_many(data=leverage_schemas)

        assert len(leverage_schemas) == len(leverages)

        got_leverages = await self.leverage_repository.get_all_leverages()

        assert len(got_leverages) == len(leverages)

        leverage_ids = set()
        for leverage in leverages:
            leverage_ids.add(leverage.id)

        for leverage in got_leverages:
            assert leverage.id in leverage_ids

    async def test_leverage_unique_constraint(
        self, database_provider_test, leverage_factory
    ):
        leverage_schemas = leverage_factory(count=1)
        for leverage in leverage_schemas:
            leverage.market = Market.BTCUSD_PERP

        with pytest.raises(IntegrityConflictException):
            await self.leverage_repository.create_many(data=leverage_schemas)
