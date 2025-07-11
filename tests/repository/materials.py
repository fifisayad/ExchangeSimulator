import pytest

from fifi import GetLogger
from faker import Faker

from src.common.portfolio_schema import PortfolioSchema


fake = Faker()
LOGGER = GetLogger().get()


@pytest.fixture
def portfolio_factory():
    def create_portfolio():
        return PortfolioSchema(name=fake.first_name())

    return create_portfolio
