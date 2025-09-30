from typing import List, Optional
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from fifi import db_async_session
from fifi.exceptions import NotExistedSessionException
from fifi.enums import Market

from ..models.leverage import Leverage
from .simulator_base_repository import SimulatorBaseRepository


class LeverageRepository(SimulatorBaseRepository):
    def __init__(self):
        super().__init__(model=Leverage)

    @db_async_session
    async def get_all_leverages(
        self,
        with_for_update: bool = False,
        session: Optional[AsyncSession] = None,
    ) -> List[Leverage]:
        if not session:
            raise NotExistedSessionException("session is not existed")
        stmt = select(self.model)

        if with_for_update:
            stmt = stmt.with_for_update()

        results = await session.execute(stmt)
        return list(results.scalars().all())

    @db_async_session
    async def get_leverage_by_portfolio_id_and_market(
        self,
        portfolio_id: str,
        market: Market,
        with_for_update: bool = False,
        session: Optional[AsyncSession] = None,
    ) -> Optional[Leverage]:
        if not session:
            raise NotExistedSessionException("session is not existed")
        stmt = select(self.model).where(
            and_(Leverage.portfolio_id == portfolio_id, Leverage.market == market)
        )

        if with_for_update:
            stmt = stmt.with_for_update()

        result = await session.execute(stmt)
        return result.unique().scalar_one_or_none()
