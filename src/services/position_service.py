from typing import Dict, List, Optional
from fifi import GetLogger

from ..enums.market import Market
from ..enums.position_status import PositionStatus
from ..models import Position
from ..repository import PositionRepository
from .service import Service


LOGGER = GetLogger().get()


class PositionService(Service):
    """Service class responsible for managing trading positions, including creation,
    merging, partial and full closure, and liquidation. It coordinates with repositories
    and other services to persist changes and manage balance updates."""

    def __init__(self) -> None:
        """Initializes the PositionService with repository and dependent services."""

        self._repo = PositionRepository()

    @property
    def repo(self) -> PositionRepository:
        return self._repo

    async def get_open_positions(self) -> List[Position]:
        """Fetches all currently open trading positions.

        Returns:
            List[Position]: A list of open positions.
        """
        return await self.repo.get_all_positions(status=PositionStatus.OPEN)

    async def get_open_positions_hashmap(self) -> Dict[str, Position]:
        """Returns a hashmap of open positions keyed by market and portfolio ID.

        Returns:
            Dict[str, Position]: A dictionary of open positions with keys in the format
            "{market}_{portfolio_id}".
        """
        open_positions = await self.get_open_positions()
        positions = dict()
        # unique hash for this is {market}_{portfolio_id}
        for position in open_positions:
            positions[f"{position.market}_{position.portfolio_id}"] = position
        return positions

    async def get_by_portfolio_and_market(
        self, portfolio_id: str, market: Market
    ) -> Optional[Position]:
        return await self._repo.get_by_portfolio_and_market(
            portfolio_id=portfolio_id, market=market
        )
