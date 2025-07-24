import pytest

from src.services import BalanceService
from tests.materials import *

LOGGER = GetLogger().get()


@pytest.mark.asyncio
class TestBalanceService:
    balance_service = BalanceService()

    async def test_create_by_qty(self, database_provider_test):
        balance = await self.balance_service.create_by_qty(
            portfolio_id=str(uuid.uuid4()), asset=Asset.BTC, qty=0.443
        )
        assert balance is not None
        got_balance = await self.balance_service.read_by_id(balance.id)
        assert got_balance is not None

        assert balance.to_dict() == got_balance.to_dict()
