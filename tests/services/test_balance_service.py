import pytest

from src.models.balance import Balance
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

    async def test_lock_balance_not_exist_portfolio_id(self, database_provider_test):
        portfolio_id = str(uuid.uuid4())
        balance = await self.balance_service.create_by_qty(
            portfolio_id=portfolio_id, asset=Asset.BTC, qty=0.443
        )
        assert balance is not None

        is_locked = await self.balance_service.lock_balance(
            portfolio_id=str(uuid.uuid4()), asset=Asset.BTC, locked_qty=0.2
        )
        assert is_locked == False

    async def test_lock_balance_two_times_lock(self, database_provider_test):
        portfolio_id = str(uuid.uuid4())
        balance = await self.balance_service.create_by_qty(
            portfolio_id=portfolio_id, asset=Asset.BTC, qty=0.443
        )
        assert balance is not None

        is_locked = await self.balance_service.lock_balance(
            portfolio_id=portfolio_id, asset=Asset.BTC, locked_qty=0.2
        )
        assert is_locked == True
        is_locked = await self.balance_service.lock_balance(
            portfolio_id=portfolio_id, asset=Asset.BTC, locked_qty=0.23
        )

        got_balance = await self.balance_service.read_by_id(balance.id)
        assert got_balance is not None

        assert round(got_balance.quantity - 0.443) == 0
        assert round(got_balance.available - 0.013) == 0
        assert round(got_balance.frozen - 0.43) == 0

    async def test_unlock_balance(
        self, database_provider_test, balance_factory_for_portfolios
    ):
        balance_schemas = balance_factory_for_portfolios(portfolio_id=str(uuid.uuid4()))
        balances: List[Balance] = await self.balance_service.create_many(
            data=balance_schemas
        )

        change_amount = 0.5
        for balance in balances:
            is_unlocked = await self.balance_service.unlock_balance(
                portfolio_id=balance.portfolio_id,
                asset=balance.asset,
                unlocked_qty=balance.frozen * change_amount,
            )

            assert is_unlocked

            updated_balance = await self.balance_service.read_by_id(id_=balance.id)

            assert updated_balance is not None
            assert round(
                updated_balance.available - balance.available, ndigits=10
            ) == round(balance.frozen * change_amount, ndigits=10)
            assert round(balance.frozen - updated_balance.frozen, ndigits=10) == round(
                balance.frozen * change_amount, ndigits=10
            )
            assert updated_balance.quantity == balance.quantity

    async def test_burn_balance(
        self, database_provider_test, balance_factory_for_portfolios
    ):
        balance_schemas = balance_factory_for_portfolios(portfolio_id=str(uuid.uuid4()))
        balances = await self.balance_service.create_many(data=balance_schemas)

        burn_portion = 0.02
        for balance in balances:
            is_burned = await self.balance_service.burn_balance(
                portfolio_id=balance.portfolio_id,
                asset=balance.asset,
                burned_qty=balance.frozen * burn_portion,
            )

            assert is_burned

            updated_balance = await self.balance_service.read_by_id(balance.id)

            assert updated_balance is not None
            assert round(balance.frozen - updated_balance.frozen, ndigits=10) == round(
                balance.frozen * burn_portion, ndigits=10
            )
            assert round(
                balance.quantity - updated_balance.quantity, ndigits=10
            ) == round(balance.frozen * burn_portion, ndigits=10)
            assert updated_balance.burned == balance.frozen * burn_portion

    async def test_add_balance(
        self, database_provider_test, balance_factory_for_portfolios
    ):
        balance_schemas = balance_factory_for_portfolios(portfolio_id=str(uuid.uuid4()))
        balances = await self.balance_service.create_many(data=balance_schemas)

        for balance in balances:
            amount = random.random()
            is_added = await self.balance_service.add_balance(
                portfolio_id=balance.portfolio_id, asset=balance.asset, qty=amount
            )
            assert is_added

            updated_balance = await self.balance_service.read_by_id(balance.id)

            assert updated_balance is not None
            assert round(
                updated_balance.quantity - balance.quantity, ndigits=10
            ) == round(amount, ndigits=10)
            assert round(
                updated_balance.available - balance.available, ndigits=10
            ) == round(amount, ndigits=10)
            assert updated_balance.frozen == balance.frozen

    async def test_check_qty(
        self, database_provider_test, balance_factory_for_portfolios
    ):
        balance_schemas = balance_factory_for_portfolios(portfolio_id=str(uuid.uuid4()))
        balances = await self.balance_service.create_many(data=balance_schemas)

        for balance in balances:
            afforded = await self.balance_service.check_available_qty(
                portfolio_id=balance.portfolio_id,
                asset=balance.asset,
                qty=balance.available,
            )
            assert afforded
            afforded = await self.balance_service.check_available_qty(
                portfolio_id=balance.portfolio_id,
                asset=balance.asset,
                qty=balance.available + random.random(),
            )
            assert not afforded

    async def test_pay_fee(
        self, database_provider_test, balance_factory_for_portfolios
    ):
        balance_schemas = balance_factory_for_portfolios(portfolio_id=str(uuid.uuid4()))
        balances = await self.balance_service.create_many(data=balance_schemas)

        fee_portion = 0.001
        for balance in balances:
            paid = await self.balance_service.pay_fee(
                portfolio_id=balance.portfolio_id,
                asset=balance.asset,
                paid_qty=balance.available * fee_portion,
            )
            assert paid

            updated_balance = await self.balance_service.read_by_id(balance.id)
            assert updated_balance is not None
            assert round(
                balance.quantity - updated_balance.quantity, ndigits=10
            ) == round(balance.available * fee_portion, ndigits=10)
            assert round(
                balance.available - updated_balance.available, ndigits=10
            ) == round(balance.available * fee_portion, ndigits=10)
            assert updated_balance.fee_paid == balance.available * fee_portion
