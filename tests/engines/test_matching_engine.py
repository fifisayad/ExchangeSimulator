import pytest

from src.common.exceptions import InvalidOrder
from src.engines.matching_engine import MatchingEngine
from src.schemas.position_schema import PositionSchema
from src.services import PositionService
from tests.materials import *


@pytest.mark.asyncio
class TestMatchingEngine:
    position_service = PositionService()
    matching_engine = MatchingEngine()

    async def test_perpetual_open_position_check(self, database_provider_test):
        checked = await self.matching_engine.perpetual_open_position_check(
            market=Market.BTCUSD_PERP,
            portfolio_id="iamrich",
            side=OrderSide.SELL,
            size=0.123,
        )
        assert not checked

        position_schema = PositionSchema(
            portfolio_id="iamrich",
            market=Market.BTCUSD_PERP,
            side=PositionSide.LONG,
            status=PositionStatus.OPEN,
            size=0.1234,
        )
        position = await self.position_service.create(data=position_schema)

        checked = await self.matching_engine.perpetual_open_position_check(
            market=Market.BTCUSD_PERP,
            portfolio_id="iamrich",
            side=OrderSide.SELL,
            size=0.1234,
        )
        assert checked

        checked = await self.matching_engine.perpetual_open_position_check(
            market=Market.BTCUSD_PERP,
            portfolio_id="iamrich",
            side=OrderSide.SELL,
            size=0.123,
        )
        assert checked

        checked = await self.matching_engine.perpetual_open_position_check(
            market=Market.ETHUSD_PERP,
            portfolio_id="iamrich",
            side=OrderSide.SELL,
            size=0.123,
        )
        assert not checked

        checked = await self.matching_engine.perpetual_open_position_check(
            market=Market.BTCUSD_PERP,
            portfolio_id="iamrich",
            side=OrderSide.BUY,
            size=0.123,
        )
        assert not checked

        with pytest.raises(InvalidOrder):
            checked = await self.matching_engine.perpetual_open_position_check(
                market=Market.BTCUSD_PERP,
                portfolio_id="iamrich",
                side=OrderSide.SELL,
                size=0.134,
            )
