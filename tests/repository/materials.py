import random
from typing import List
import pytest

from fifi import GetLogger
from faker import Faker

from src.enums.asset import Asset
from src.schemas import PortfolioSchema
from src.schemas import BalanceSchema


fake = Faker()
LOGGER = GetLogger().get()


@pytest.fixture
def portfolio_factory():
    def create_portfolio():
        return PortfolioSchema(name=fake.first_name())

    return create_portfolio


@pytest.fixture
def balance_factory_for_portfolios():
    def create_balance(portfolio_id: str) -> List[BalanceSchema]:
        balances = list()
        for asset in Asset:
            portion = [1, 2, 3, 4, 5]
            quantity = random.random()
            available = quantity / random.choice(portion)
            balances.append(
                BalanceSchema(
                    portfolio_id=portfolio_id,
                    asset=asset,
                    quantity=quantity,
                    available=available,
                    frozen=quantity - available,
                    leverage=random.choice(portion),
                )
            )
        return balances

    return create_balance
