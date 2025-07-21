from typing import List, Optional
from fifi import db_async_session
from fifi.exceptions import NotExistedSessionException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..enums.asset import Asset
from .simulator_base_repository import SimulatorBaseRepository
from ..models.balance import Balance


class BalanceRepository(SimulatorBaseRepository):
    """
    Repository class for handling database operations related to the Balance model.

    Provides asynchronous methods to retrieve all balances or balances associated with a specific
    portfolio ID. Supports optional row-level locking using SQL's FOR UPDATE clause.

    Attributes:
        model (Type[Balance]): The SQLAlchemy model associated with this repository.
    """

    def __init__(self):
        super().__init__(model=Balance)

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
    async def get_portfolio_asset(
        self,
        portfolio_id: str,
        asset: Asset,
        with_for_update: bool = False,
        session: Optional[AsyncSession] = None,
    ) -> Optional[Balance]:
        """
        Retrieve a specific asset balance from a portfolio.

        This asynchronous method queries the database for a `Balance` entry that matches
        the given `portfolio_id` and `asset`. Optionally, the query can be locked for
        update to prevent concurrent modifications.

        Args:
            portfolio_id (str): The ID of the portfolio to search within.
            asset (Asset): The asset to retrieve the balance for.
            with_for_update (bool, optional): If True, adds a "FOR UPDATE" clause to
                the SQL statement to lock the selected row. Defaults to False.
            session (Optional[AsyncSession], optional): An optional SQLAlchemy async
                session. If not provided, an exception will be raised.

        Returns:
            Optional[Balance]: The `Balance` object if found, otherwise `None`.

        Raises:
            NotExistedSessionException: If no session is provided.
        """
        if not session:
            raise NotExistedSessionException("session is not existed")
        stmt = select(self.model).where(
            and_(Balance.portfolio_id == portfolio_id, Balance.asset == asset)
        )

        if with_for_update:
            stmt = stmt.with_for_update()

        result = await session.execute(stmt)
        return result.unique().scalar_one_or_none()
