from typing import Optional
from ..models import Portfolio
from .service import Service
from ..repository import PortfolioRepository


class PortfolioService(Service):
    def __init__(self) -> None:
        self._repo = PortfolioRepository()

    @property
    def repo(self) -> PortfolioRepository:
        return self._repo

    async def read_by_name(self, name: str) -> Optional[Portfolio]:
        return await self.repo.get_by_name(name=name)
