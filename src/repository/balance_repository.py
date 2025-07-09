from typing import List, Optional
from fifi import Repository, db_async_session
from fifi.exceptions import NotExistedSessionException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.balance import Balance


class BalanceRepository(Repository):

    model = Balance

    @db_async_session
    async def get_all_balances(
        self,
        with_for_update: bool = False,
        session: Optional[AsyncSession] = None,
    ) -> List[Balance]:
        if not session:
            raise NotExistedSessionException("session is not existed")
        stmt = select(self.model)

        if with_for_update:
            stmt = stmt.with_for_update()

        results = await session.execute(stmt)
        return list(results.scalars().all())

    @db_async_session
    async def get_balances_by_portfolio_id(
        self,
        portfolio_id: str,
        with_for_update: bool = False,
        session: Optional[AsyncSession] = None,
    ) -> List[Balance]:
        if not session:
            raise NotExistedSessionException("session is not existed")
        stmt = select(self.model).where(self.model.portfolio_id == portfolio_id)

        if with_for_update:
            stmt = stmt.with_for_update()

        results = await session.execute(stmt)
        return list(results.scalars().all())
