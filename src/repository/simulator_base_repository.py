from typing import List, Optional
from fifi import DecoratedBase, Repository, db_async_session
from fifi.exceptions import NotExistedSessionException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class SimulatorBaseRepository(Repository):
    @db_async_session
    async def get_entities_by_portfolio_id(
        self,
        portfolio_id: str,
        with_for_update: bool = False,
        session: Optional[AsyncSession] = None,
    ) -> List[DecoratedBase]:
        if not session:
            raise NotExistedSessionException("session is not existed")
        stmt = select(self.model).where(self.model.portfolio_id == portfolio_id)

        if with_for_update:
            stmt = stmt.with_for_update()

        results = await session.execute(stmt)
        return list(results.scalars().all())
