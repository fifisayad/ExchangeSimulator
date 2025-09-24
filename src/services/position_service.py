import logging
from typing import Dict, List, Optional
from fifi import BaseService

from ..enums.position_side import PositionSide
from ..enums.market import Market
from ..enums.position_status import PositionStatus
from ..models import Position
from ..repository import PositionRepository


LOGGER = logging.getLogger(__name__)


class PositionService(BaseService):
    """Service class responsible for managing trading positions, including creation,
    merging, partial and full closure, and liquidation. It coordinates with repositories
    and other services to persist changes and manage balance updates."""

    def __init__(self) -> None:
        """Initializes the PositionService with repository and dependent services."""

        self._repo = PositionRepository()

    @property
    def repo(self) -> PositionRepository:
        return self._repo

    async def get_positions(
        self,
        portfolio_id: Optional[str] = None,
        market: Optional[Market] = None,
        status: Optional[PositionStatus] = None,
        side: Optional[PositionSide] = None,
    ) -> List[Position]:
        return await self.repo.get_all_positions(
            portfolio_id=portfolio_id, market=market, status=status, side=side
        )

    async def get_open_positions(self) -> List[Position]:
        """Fetches all currently open trading positions.

        Returns:
            List[Position]: A list of open positions.
        """
        return await self.get_positions(status=PositionStatus.OPEN)

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
