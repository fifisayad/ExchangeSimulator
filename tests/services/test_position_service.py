from typing import Set
from fifi.helpers.get_current_time import GetCurrentTime
import pytest

from src.models import Position
from src.services import PositionService
from tests.materials import *

LOGGER = GetLogger().get()


@pytest.mark.asyncio
class TestPositionService:
    position_service = PositionService()

    async def test_get_positions(self, database_provider_test, position_factory):
        positions_schemas: List[PositionSchema] = position_factory()
        positions = await self.position_service.create_many(data=positions_schemas)

        positions_id_set = set()
        for position in positions:
            positions_id_set.add(position.id)

        got_positions = await self.position_service.get_positions()

        for position in got_positions:
            assert position.id in positions_id_set

    async def test_get_positions_with_portfolio_id(
        self, database_provider_test, position_factory
    ):
        portfolio_counts = 5
        position_counts = 10
        positions_schemas: List[PositionSchema] = list()
        positions_portfolio_ids: Set[str] = set()
        for i in range(portfolio_counts):
            portfolio_id = str(uuid.uuid4())
            positions_portfolio_ids.add(portfolio_id)
            positions_schemas += position_factory(
                portfolio_id=portfolio_id, count=position_counts
            )
        positions: List[Position] = await self.position_service.create_many(
            data=positions_schemas
        )
        assert len(positions) == portfolio_counts * position_counts
        LOGGER.info(f"positions counts: {len(positions)}")

        for portfolio_id in positions_portfolio_ids:
            got_positions = await self.position_service.get_positions(
                portfolio_id=portfolio_id
            )
            assert len(got_positions) == position_counts

            for position in got_positions:
                assert position.portfolio_id == portfolio_id

    async def test_get_positions_with_status(
        self, database_provider_test, position_factory
    ):
        positions_schemas: List[PositionSchema] = position_factory(count=100)
        positions: List[Position] = await self.position_service.create_many(
            data=positions_schemas
        )

        active_positions_id_set = set()
        for position in positions:
            if position.status == PositionStatus.OPEN:
                active_positions_id_set.add(position.id)

        LOGGER.info(f"active positions counts: {len(active_positions_id_set)}")

        got_positions = await self.position_service.get_positions(
            status=PositionStatus.OPEN
        )

        for position in got_positions:
            assert position.id in active_positions_id_set

    async def test_get_positions_with_side(
        self, database_provider_test, position_factory
    ):
        positions_schemas: List[PositionSchema] = position_factory(count=100)
        positions: List[Position] = await self.position_service.create_many(
            data=positions_schemas
        )

        long_positions_id_set = set()
        for position in positions:
            if position.side == PositionSide.LONG:
                long_positions_id_set.add(position.id)

        LOGGER.info(f"long positions counts: {len(long_positions_id_set)}")

        got_positions = await self.position_service.get_positions(
            side=PositionSide.LONG
        )

        for position in got_positions:
            assert position.id in long_positions_id_set

    async def test_get_positions_with_market(
        self, database_provider_test, position_factory
    ):
        positions_schemas: List[PositionSchema] = position_factory(count=100)
        positions: List[Position] = await self.position_service.create_many(
            data=positions_schemas
        )

        btc_perp_positions_id_set = set()
        for position in positions:
            if position.market == Market.BTCUSD_PERP:
                btc_perp_positions_id_set.add(position.id)

        LOGGER.info(f"BTCUSD_PERP positions counts: {len(btc_perp_positions_id_set)}")

        got_positions = await self.position_service.get_positions(
            market=Market.BTCUSD_PERP
        )

        for position in got_positions:
            assert position.id in btc_perp_positions_id_set

    async def test_get_positions_with_all_filters(
        self, database_provider_test, position_factory
    ):
        portfolio_id = str(uuid.uuid4())
        positions_schemas: List[PositionSchema] = position_factory(
            portfolio_id=portfolio_id, count=200
        )
        positions_schemas += position_factory(count=200)
        positions: List[Position] = await self.position_service.create_many(
            data=positions_schemas
        )

        positions_id_set = set()
        for position in positions:
            if (
                position.market == Market.BTCUSD_PERP
                and position.side == PositionSide.LONG
                and position.status == PositionStatus.OPEN
                and position.portfolio_id == portfolio_id
            ):
                positions_id_set.add(position.id)

        LOGGER.info(f"BTCUSD_PERP positions counts: {len(positions_id_set)}")

        got_positions = await self.position_service.get_positions(
            side=PositionSide.LONG,
            status=PositionStatus.OPEN,
            market=Market.BTCUSD_PERP,
            portfolio_id=portfolio_id,
        )

        for position in got_positions:
            assert position.id in positions_id_set

    async def test_get_open_positions_hashmap(
        self, database_provider_test, open_position_factory
    ):
        positions_schemas: List[PositionSchema] = open_position_factory(count=100)
        positions = await self.position_service.create_many(data=positions_schemas)

        open_positions_hash_map = dict()
        for position in positions:
            if position.status == PositionStatus.OPEN:
                open_positions_hash_map[
                    f"{position.market}_{position.portfolio_id}"
                ] = position

        LOGGER.info(f"{len(open_positions_hash_map)=}")
        got_open_positions_hashmap = (
            await self.position_service.get_open_positions_hashmap()
        )
        LOGGER.info(f"{len(got_open_positions_hashmap)=} by service")

        assert len(open_positions_hash_map) == len(got_open_positions_hashmap)
        for hash_id, open_position in got_open_positions_hashmap.items():
            assert hash_id in open_positions_hash_map
            assert open_position.to_dict() == open_positions_hash_map[hash_id].to_dict()
