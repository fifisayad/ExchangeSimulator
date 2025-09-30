from typing import List, Optional
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from fifi import db_async_session
from fifi.exceptions import NotExistedSessionException
from fifi.enums import PositionSide, PositionStatus, Market

from .simulator_base_repository import SimulatorBaseRepository
from ..models.position import Position


class PositionRepository(SimulatorBaseRepository):
    """
    Repository for managing Position entities in the simulator context.

    Inherits from:
        SimulatorBaseRepository: A base repository class customized for simulator-related models.

    This repository provides database access methods specific to the Position model.
    """

    def __init__(self):
        super().__init__(model=Position)

    @db_async_session
    async def get_all_positions(
        self,
        portfolio_id: Optional[str] = None,
        market: Optional[Market] = None,
        status: Optional[PositionStatus] = None,
        side: Optional[PositionSide] = None,
        with_for_update: bool = False,
        session: Optional[AsyncSession] = None,
    ) -> List[Position]:
        """
        Retrieve all Position records filtered by optional status, side, and market parameters.

        Args:
            status (Optional[PositionStatus]): Filter positions by their status (e.g., OPEN, CLOSED).
            side (Optional[PositionSide]): Filter positions by their side (e.g., LONG, SHORT).
            market (Optional[Market]): Filter positions by market.
            with_for_update (bool, optional): If True, locks selected rows for update. Defaults to False.
            session (Optional[AsyncSession]): SQLAlchemy asynchronous session. If not provided, an exception is raised.

        Returns:
            List[Position]: A list of Position objects matching the specified filters.

        Raises:
            NotExistedSessionException: If the session is not provided.
        """
        if not session:
            raise NotExistedSessionException("session is not existed")
        stmt = select(self.model)
        if portfolio_id:
            stmt = stmt.where(Position.portfolio_id == portfolio_id)
        if status:
            stmt = stmt.where(Position.status == status)
        if side:
            stmt = stmt.where(Position.side == side)
        if market:
            stmt = stmt.where(Position.market == market)

        if with_for_update:
            stmt = stmt.with_for_update()

        results = await session.execute(stmt)
        return list(results.scalars().all())

    @db_async_session
    async def get_by_portfolio_and_market(
        self,
        portfolio_id: str,
        market: Market,
        with_for_update: bool = False,
        session: Optional[AsyncSession] = None,
    ) -> Optional[Position]:
        if not session:
            raise NotExistedSessionException("session is not existed")
        stmt = select(self.model).where(
            and_(Position.market == market, Position.portfolio_id == portfolio_id)
        )
        if with_for_update:
            stmt = stmt.with_for_update()

        results = await session.execute(stmt)
        return results.unique().scalar_one_or_none()
