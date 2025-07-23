from typing import List, Union
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from contextlib import asynccontextmanager

from ...schemas.balance_schema import (
    BalanceDepositSchema,
    BalanceReadSchema,
    BalanceResponseSchema,
)
from .deps import get_balance_service, get_portfolio_service
from ...services import BalanceService, PortfolioService


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
        if balance_query.asset:
            return await balance_service.read_by_asset(
                portfolio_id=balance_query.portfolio_id, asset=balance_query.asset
            )
        return await balance_service.read_many_by_portfolio_id(
            portfolio_id=balance_query.portfolio_id
        )
    raise HTTPException(status_code=404, detail="balance not found")


@balance_router.post("/deposit", response_model=BalanceResponseSchema)
async def deposit_balance(
    balance_dposit: BalanceDepositSchema,
    balance_service: BalanceService = Depends(get_balance_service),
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    is_successful = await balance_service.add_balance(
        portfolio_id=balance_dposit.portfolio_id,
        asset=balance_dposit.asset,
        qty=balance_dposit.quantity,
    )
    if is_successful:
        return await balance_service.read_by_asset(
            portfolio_id=balance_dposit.portfolio_id, asset=balance_dposit.asset
        )
    else:
        portfolio = await portfolio_service.read_by_id(id=balance_dposit.portfolio_id)
        if portfolio:
            return await balance_service.create_by_qty(
                portfolio_id=balance_dposit.portfolio_id,
                asset=balance_dposit.asset,
                qty=balance_dposit.quantity,
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"the portfolio {balance_dposit.portfolio_id=} not existed",
            )
