import pytest

from src.models import Position
from src.repository import PositionRepository
from src.enums.asset import Asset
from tests.materials import *


@pytest.mark.asyncio
class TestSimulatorBaseRepository:
    position_repo = PositionRepository()

    async def test_get_entity_by_portfolio_id(
        self, database_provider_test, position_factory
    ):
        newyork_positions_schemas: List[PositionSchema] = position_factory(
            portfolio_id="newyork"
        )

        tehran_positions_schemas: List[PositionSchema] = position_factory(
            portfolio_id="tehran"
        )

        positions: List[Position] = await self.position_repo.create_many(
            data=tehran_positions_schemas + newyork_positions_schemas,
            return_models=True,
        )

        newyork_positions = await self.position_repo.get_entities_by_portfolio_id(
            portfolio_id="newyork"
        )

        assert len(newyork_positions_schemas) == len(newyork_positions)

    async def test_get_entity_by_portfolio_id_not_exist(
        self, database_provider_test, position_factory
    ):
        tehran_positions_schemas: List[PositionSchema] = position_factory(
            portfolio_id="tehran"
        )

        positions: List[Position] = await self.position_repo.create_many(
            data=tehran_positions_schemas,
            return_models=True,
        )

        newyork_positions = await self.position_repo.get_entities_by_portfolio_id(
            portfolio_id="newyork"
        )

        assert len(newyork_positions) == 0
