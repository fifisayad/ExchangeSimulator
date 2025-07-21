import pytest

from src.repository import PositionRepository
from tests.repository.materials import *


@pytest.mark.asyncio
class TestpositionRepository:
    position_repo = PositionRepository()

    async def test_get_all_positions(self, database_provider_test, position_factory):
        positions_schemas: List[PositionSchema] = position_factory()
        positions = await self.position_repo.create_many(
            data=positions_schemas, return_models=True
        )

        positions_id_set = set()
        for position in positions:
            positions_id_set.add(position.id)

        got_positions = await self.position_repo.get_all_positions()

        for position in got_positions:
            assert position.id in positions_id_set
