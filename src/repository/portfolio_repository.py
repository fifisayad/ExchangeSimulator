from typing import Optional
from fifi import Repository

from ..models.portfolio import Portfolio


class PortfolioRepository(Repository):
    """
    Repository class for managing Portfolio-related operations.

    This Repository provides asynchronous methods to create, retrieve, and delete portfolio
    records, as well as fetch associated balances. It uses a repository pattern for data access.

    Attributes:
        portfolio_repo (Repository): Repository instance for Portfolio model interactions.
    """

    def __init__(self):
        super().__init__(model=Portfolio)

    async def get_by_name(self, name: str) -> Optional[Portfolio]:
        """
        Retrieve a portfolio using its name.

        Args:
            name (str): The name of the portfolio.

        Returns:
            Optional[Portfolio]: The matching portfolio if found, otherwise None.
        """
        return await self.get_one_by_id(id_=name, column="name")

    async def remove_by_name(self, name: str) -> int:
        """
        Remove a portfolio identified by name.

        Args:
            name (Optional[str]): The name of the portfolio to remove.

        Raises:
            ValueError: If name is not provided.

        Returns:
            int: The number of records deleted (typically 1 if successful, 0 otherwise).
        """
        return await self.remove_by_id(id_=name, column="name")
