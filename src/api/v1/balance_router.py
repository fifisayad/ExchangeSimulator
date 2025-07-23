from typing import List, Union
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from contextlib import asynccontextmanager

from ...schemas.balance_schema import BalanceReadSchema, BalanceResponseSchema
from .deps import get_balance_service
from ...services import BalanceService


@asynccontextmanager
async def lifespan(app: FastAPI):
    # initialize
    yield
    # cleanup


balance_router = APIRouter(prefix="/balance", tags=["Balance"], lifespan=lifespan)


@balance_router.get(
    "", response_model=Union[BalanceResponseSchema, List[BalanceResponseSchema]]
)
async def get_balance(
    balance_query: BalanceReadSchema,
    balance_service: BalanceService = Depends(get_balance_service),
):
    if balance_query.id:
        balance = await balance_service.read_by_id(id=balance_query.id)
        if balance:
            return balance
    if balance_query.portfolio_id:
        balances = await balance_service.read_many_by_portfolio_id(
            portfolio_id=balance_query.portfolio_id
        )
        if balance_query.asset:
            for balance in balances:
                if balance.asset == balance_query.asset:
                    return balance
        return balances
    raise HTTPException(status_code=404, detail="balance not found")
