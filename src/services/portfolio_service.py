from typing import List, Optional
from fifi import Repository

from src.schemas.portfolio_schema import PortfolioSchema
from ..models.portfolio import Portfolio
from ..models.balance import Balance


class PortfolioService:
    """
    Service class for managing Portfolio-related operations.

    This service provides asynchronous methods to create, retrieve, and delete portfolio
    records, as well as fetch associated balances. It uses a repository pattern for data access.

    Attributes:
        portfolio_repo (Repository): Repository instance for Portfolio model interactions.
    """

    def __init__(self):
        """
        Initialize the PortfolioService with a repository for the Portfolio model.
        """
        self.portfolio_repo = Repository(Portfolio)

    async def get_portfolio_by_id(self, id: str) -> Optional[Portfolio]:
        """
        Retrieve a portfolio using its unique identifier.

        Args:
            id (str): The unique ID of the portfolio.

        Returns:
            Optional[Portfolio]: The matching portfolio if found, otherwise None.
        """
        return await self.portfolio_repo.get_one_by_id(id_=id)

    async def get_portfolio_by_name(self, name: str) -> Optional[Portfolio]:
        """
        Retrieve a portfolio using its name.

        Args:
            name (str): The name of the portfolio.

        Returns:
            Optional[Portfolio]: The matching portfolio if found, otherwise None.
        """
        return await self.portfolio_repo.get_one_by_id(id_=name, column="name")

    async def create_portfolio(self, name: str) -> Optional[Portfolio]:
        """
        Create a new portfolio with the specified name.

        Args:
            name (str): The name for the new portfolio.

        Returns:
            Optional[Portfolio]: The created portfolio instance if successful, otherwise None.
        """
        new_portfolio = PortfolioSchema(name=name)
        return await self.portfolio_repo.create(data=new_portfolio)

    async def get_portfolio_balances(
        self, id: Optional[str], name: Optional[str]
    ) -> Optional[List[Balance]]:
        """
        Retrieve the balances associated with a portfolio, identified by either ID or name.

        Args:
            id (Optional[str]): The ID of the portfolio.
            name (Optional[str]): The name of the portfolio.

        Raises:
            ValueError: If neither ID nor name is provided.

        Returns:
            Optional[List[Balance]]: A list of balances if the portfolio exists, otherwise None.
        """
        if not id and not name:
            raise ValueError("One of id or name argument must be gave!")
        if id:
            portfolio = await self.get_portfolio_by_id(id=id)
        elif name:
            portfolio = await self.get_portfolio_by_name(name=name)
        else:
            return None
        if portfolio:
            return portfolio.balances

    async def remove_portfolio(self, id: Optional[str], name: Optional[str]) -> int:
        """
        Remove a portfolio identified by either ID or name.

        Args:
            id (Optional[str]): The ID of the portfolio to remove.
            name (Optional[str]): The name of the portfolio to remove.

        Raises:
            ValueError: If neither ID nor name is provided.

        Returns:
            int: The number of records deleted (typically 1 if successful, 0 otherwise).
        """
        if not id and not name:
            raise ValueError("One of id or name argument must be gave!")
        if id:
            return await self.portfolio_repo.remove_by_id(id_=id)
        elif name:
            return await self.portfolio_repo.remove_by_id(id_=name, column="name")
        else:
            return 0
