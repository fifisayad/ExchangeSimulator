import random
import uuid
import pytest
from typing import List

from fifi.helpers.get_logger import LoggerFactory
from fifi.enums import (
    Market,
    Asset,
    OrderSide,
    OrderStatus,
    PositionSide,
    PositionStatus,
)
from faker import Faker
from src.schemas import PortfolioSchema, BalanceSchema, OrderSchema, LeverageSchema
from src.common.settings import Setting
from src.schemas.position_schema import PositionSchema


fake = Faker()
setting = Setting()
LOGGER = LoggerFactory().get(__name__)


@pytest.fixture
def portfolio_factory():
    def create_portfolio():
        return PortfolioSchema(name=str(fake.random_letters(10)))

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


@pytest.fixture
def position_factory():
    def create_positions(
        portfolio_id: str = "iamrich", count: int = 5
    ) -> List[PositionSchema]:
        position_schemas = list()
        leverages = [1, 2, 3, 4, 5]
        for i in range(count):
            position_schemas.append(
                PositionSchema(
                    market=fake.enum(Market),
                    portfolio_id=portfolio_id,
                    side=fake.enum(PositionSide),
                    entry_price=random.random(),
                    status=fake.enum(PositionStatus),
                    margin=random.random(),
                    size=random.random(),
                    leverage=random.choice(leverages),
                    lqd_price=random.random(),
                )
            )
        return position_schemas

    return create_positions


@pytest.fixture
def open_position_factory():
    def create_positions(count: int = 5) -> List[PositionSchema]:
        position_schemas = list()
        leverages = [1, 2, 3, 4, 5]
        for i in range(count):
            position_schemas.append(
                PositionSchema(
                    market=fake.enum(Market),
                    portfolio_id=str(uuid.uuid4()),
                    side=fake.enum(PositionSide),
                    entry_price=random.random(),
                    status=fake.enum(PositionStatus),
                    margin=random.random(),
                    size=random.random(),
                    leverage=random.choice(leverages),
                    lqd_price=random.random(),
                )
            )
        return position_schemas

    return create_positions


@pytest.fixture
def leverage_factory():
    def create_leverage(count: int = 5) -> List[LeverageSchema]:
        leverage_schemas = list()
        leverages = [1, 2, 3, 4, 5]
        for i in range(count):
            portfolio_id = str(uuid.uuid4())
            for market in Market:
                leverage_schemas.append(
                    LeverageSchema(
                        portfolio_id=portfolio_id,
                        market=market,
                        leverage=random.choice(leverages),
                    )
                )
        return leverage_schemas

    return create_leverage
