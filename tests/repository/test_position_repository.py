import pytest

from src.models import Position
from src.repository import PositionRepository
from tests.materials import *


@pytest.mark.asyncio
class TestpositionRepository:
    position_repo = PositionRepository()

    async def test_get_all_positions(self, database_provider_test, position_factory):
        positions_schemas: List[PositionSchema] = position_factory()
        positions = await self.position_repo.create_many(data=positions_schemas)

        positions_id_set = set()
        for position in positions:
            positions_id_set.add(position.id)

        got_positions = await self.position_repo.get_all_positions()

        for position in got_positions:
            assert position.id in positions_id_set

    async def test_get_all_positions_with_status(
        self, database_provider_test, position_factory
    ):
        positions_schemas: List[PositionSchema] = position_factory(count=100)
        positions: List[Position] = await self.position_repo.create_many(
            data=positions_schemas
        )

        active_positions_id_set = set()
        for position in positions:
            if position.status == PositionStatus.OPEN:
                active_positions_id_set.add(position.id)

        LOGGER.info(f"active positions counts: {len(active_positions_id_set)}")

        got_positions = await self.position_repo.get_all_positions(
            status=PositionStatus.OPEN
        )

        for position in got_positions:
            assert position.id in active_positions_id_set

    async def test_get_all_positions_with_side(
        self, database_provider_test, position_factory
    ):
        positions_schemas: List[PositionSchema] = position_factory(count=100)
        positions: List[Position] = await self.position_repo.create_many(
            data=positions_schemas
        )

        long_positions_id_set = set()
        for position in positions:
            if position.side == PositionSide.LONG:
                long_positions_id_set.add(position.id)

        LOGGER.info(f"long positions counts: {len(long_positions_id_set)}")

        got_positions = await self.position_repo.get_all_positions(
            side=PositionSide.LONG
        )

        for position in got_positions:
            assert position.id in long_positions_id_set

    async def test_get_all_positions_with_market(
        self, database_provider_test, position_factory
    ):
        positions_schemas: List[PositionSchema] = position_factory(count=100)
        positions: List[Position] = await self.position_repo.create_many(
            data=positions_schemas
        )

        btc_perp_positions_id_set = set()
        for position in positions:
            if position.market == Market.BTCUSD_PERP:
                btc_perp_positions_id_set.add(position.id)

        LOGGER.info(f"BTCUSD_PERP positions counts: {len(btc_perp_positions_id_set)}")

        got_positions = await self.position_repo.get_all_positions(
            market=Market.BTCUSD_PERP
        )

        for position in got_positions:
            assert position.id in btc_perp_positions_id_set

    async def test_get_all_positions_with_all_filters(
        self, database_provider_test, position_factory
    ):
        positions_schemas: List[PositionSchema] = position_factory(count=500)
        positions: List[Position] = await self.position_repo.create_many(
            data=positions_schemas
        )

        positions_id_set = set()
        for position in positions:
            if (
                position.market == Market.BTCUSD_PERP
                and position.side == PositionSide.LONG
                and position.status == PositionStatus.OPEN
            ):
                positions_id_set.add(position.id)

        LOGGER.info(f"BTCUSD_PERP positions counts: {len(positions_id_set)}")

        got_positions = await self.position_repo.get_all_positions(
            side=PositionSide.LONG,
            status=PositionStatus.OPEN,
            market=Market.BTCUSD_PERP,
        )

        for position in got_positions:
            assert position.id in positions_id_set
