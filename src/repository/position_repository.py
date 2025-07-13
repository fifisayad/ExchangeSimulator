from typing import List, Optional
from fifi import db_async_session
from fifi.exceptions import NotExistedSessionException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .repository.simulator_base_repository import SimulatorBaseRepository
from ..models.position import Position
from ..enums.position_side import PositionSide
from ..enums.market import Market
from ..enums.position_status import PositionStatus


class PositionRepository(SimulatorBaseRepository):
    def __init__(self):
        super().__init__(model=Position)

    @db_async_session
    async def get_all_positions(
        self,
        status: Optional[PositionStatus],
        side: Optional[PositionSide],
        market: Optional[Market],
        with_for_update: bool = False,
        session: Optional[AsyncSession] = None,
    ) -> List[Position]:
        if not session:
            raise NotExistedSessionException("session is not existed")
        stmt = select(self.model)
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
