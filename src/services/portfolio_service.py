from .service import Service
from ..repository import PortfolioRepository


class PortfolioService(Service):
    def __init__(self) -> None:
        self._repo = PortfolioRepository()

    @property
    def repo(self) -> PortfolioRepository:
        return self._repo
