import random
from typing import List
import pytest

from fifi import GetLogger
from faker import Faker

from src.enums.asset import Asset
from src.enums.market import Market
from src.enums.order_side import OrderSide
from src.enums.order_status import OrderStatus
from src.schemas import PortfolioSchema, BalanceSchema, OrderSchema
from src.common.settings import Setting


fake = Faker()
setting = Setting()
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


@pytest.fixture
def order_factory():
    def create_orders(
        portfolio_id: str = "iamrich", count: int = 5
    ) -> List[OrderSchema]:
        order_schemas = list()
        for i in range(count):
            order_schemas.append(
                OrderSchema(
                    portfolio_id=portfolio_id,
                    market=fake.enum(Market),
                    price=random.random(),
                    size=random.random(),
                    fee=random.random(),
                    side=fake.enum(OrderSide),
                    status=fake.enum(OrderStatus),
                )
            )
        return order_schemas

    return create_orders
