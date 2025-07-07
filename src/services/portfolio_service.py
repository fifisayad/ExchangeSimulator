from typing import List, Optional
from fifi import Repository

from src.schemas.portfolio_schema import PortfolioSchema
from ..models.portfolio import Portfolio
from ..models.balance import Balance


class PortfolioService:
    def __init__(self):
        self.portfolio_repo = Repository(Portfolio)

    async def get_portfolio_by_id(self, id: str) -> Optional[Portfolio]:
        return await self.portfolio_repo.get_one_by_id(id_=id)

    async def get_portfolio_by_name(self, name: str) -> Optional[Portfolio]:
        return await self.portfolio_repo.get_one_by_id(id_=name, column="name")

    async def create_portfolio(self, name: str) -> Optional[Portfolio]:
        new_portfolio = PortfolioSchema(name=name)
        return await self.portfolio_repo.create(data=new_portfolio)

    async def get_portfolio_balances(
        self, id: Optional[str], name: Optional[str]
    ) -> Optional[List[Balance]]:
        if not id and not name:
            raise ValueError("One of id or name argument must be gave!")
        if id:
            portfolio = await self.get_portfolio_by_id(id=id)
        elif name:
            portfolio = await self.get_portfolio_by_name(name=name)
        else:
            return None
        if portfolio:
            return portfolio.balances

    async def remove_portfolio(self, id: Optional[str], name: Optional[str]) -> int:
        if not id and not name:
            raise ValueError("One of id or name argument must be gave!")
        if id:
            return await self.portfolio_repo.remove_by_id(id_=id)
        elif name:
            return await self.portfolio_repo.remove_by_id(id_=name, column="name")
        else:
            return 0
