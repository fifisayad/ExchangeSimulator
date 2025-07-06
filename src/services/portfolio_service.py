from typing import Optional
from fifi import Repository
from ..models.portfolio import Portfolio


class PortfolioService:
    def __init__(self):
        self.portfolio_repo = Repository(Portfolio)

    async def get_portfolio_by_id(self, id: str) -> Optional[Portfolio]:
        return await self.portfolio_repo.get_one_by_id(id_=id)

    async def get_portfolio_by_name(self, name: str) -> Optional[Portfolio]:
        return await self.portfolio_repo.get_one_by_id(id_=name, column="name")
