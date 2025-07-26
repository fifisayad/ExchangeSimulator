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

    async def test_lock_balance(self, database_provider_test):
        portfolio_id = str(uuid.uuid4())
        balance = await self.balance_service.create_by_qty(
            portfolio_id=portfolio_id, asset=Asset.BTC, qty=0.443
        )
        assert balance is not None

        is_locked = await self.balance_service.lock_balance(
            portfolio_id=portfolio_id, asset=Asset.BTC, locked_qty=0.2
        )
        assert is_locked == True

        got_balance = await self.balance_service.read_by_id(balance.id)
        assert got_balance is not None

        assert got_balance.quantity == 0.443
        assert got_balance.available == 0.243
        assert got_balance.frozen == 0.2
