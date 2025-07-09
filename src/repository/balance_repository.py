from typing import List, Optional
from fifi import Repository, db_async_session
from fifi.exceptions import NotExistedSessionException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.balance import Balance


class BalanceRepository(Repository):
    """
    Repository class for handling database operations related to the Balance model.

    Provides asynchronous methods to retrieve all balances or balances associated with a specific
    portfolio ID. Supports optional row-level locking using SQL's FOR UPDATE clause.

    Attributes:
        model (Type[Balance]): The SQLAlchemy model associated with this repository.
    """

    model = Balance

    @db_async_session
    async def get_all_balances(
        self,
        with_for_update: bool = False,
        session: Optional[AsyncSession] = None,
    ) -> List[Balance]:
        """
        Retrieve all balance records from the database.

        Args:
            with_for_update (bool, optional): If True, applies row-level locking using FOR UPDATE.
                Defaults to False.
            session (Optional[AsyncSession], optional): An optional SQLAlchemy AsyncSession.
                If not provided, one must be supplied via the db_async_session decorator.

        Returns:
            List[Balance]: A list of all Balance instances.

        Raises:
            NotExistedSessionException: If no active session is available or provided.
        """
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
        """
        Retrieve all balance records associated with a specific portfolio ID.

        Args:
            portfolio_id (str): The portfolio ID used to filter balance records.
            with_for_update (bool, optional): If True, applies row-level locking using FOR UPDATE.
                Defaults to False.
            session (Optional[AsyncSession], optional): An optional SQLAlchemy AsyncSession.
                If not provided, one must be supplied via the db_async_session decorator.

        Returns:
            List[Balance]: A list of Balance instances matching the portfolio ID.

        Raises:
            NotExistedSessionException: If no active session is available or provided.
        """
        if not session:
            raise NotExistedSessionException("session is not existed")
        stmt = select(self.model).where(self.model.portfolio_id == portfolio_id)

        if with_for_update:
            stmt = stmt.with_for_update()

        results = await session.execute(stmt)
        return list(results.scalars().all())
