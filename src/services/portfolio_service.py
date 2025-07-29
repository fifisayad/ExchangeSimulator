from typing import Optional
from fifi import BaseService

from ..schemas.portfolio_schema import PortfolioSchema
from ..models import Portfolio
from ..repository import PortfolioRepository


class PortfolioService(BaseService):
    def __init__(self) -> None:
        self._repo = PortfolioRepository()

    @property
    def repo(self) -> PortfolioRepository:
        return self._repo

    async def read_by_name(self, name: str) -> Optional[Portfolio]:
        return await self.repo.get_by_name(name=name)

    async def update_by_name(self, name: str, data: PortfolioSchema) -> Portfolio:
        return await self.repo.update_by_id(data=data, id_=name, column="name")
