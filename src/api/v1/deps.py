from ...services import PortfolioService, BalanceService


def get_portfolio_service() -> PortfolioService:
    return PortfolioService()


def get_balance_service() -> BalanceService:
    return BalanceService()
