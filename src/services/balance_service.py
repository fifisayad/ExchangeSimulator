from ..models import Order
from ..repository import BalanceRepository


class BalanceService:

    def __init__(self):
        self.balance_repo = BalanceRepository()

    async def update_balances(self, order: Order) -> None:
        pass
