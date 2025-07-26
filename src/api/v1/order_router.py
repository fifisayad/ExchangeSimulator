from typing import List, Union
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from contextlib import asynccontextmanager

from ...common.exceptions import InvalidOrder
from ...engines.matching_engine import MatchingEngine
from ...schemas.order_schema import (
    OrderCreateSchema,
    OrderReadSchema,
    OrderResponseSchema,
)
from .deps import get_order_service, get_matching_engine
from ...services import OrderService


@asynccontextmanager
async def lifespan(app: FastAPI):
    # initialize
    yield
    # cleanup


order_router = APIRouter(prefix="/order", tags=["Order"], lifespan=lifespan)


@order_router.get(
    "", response_model=Union[OrderResponseSchema, List[OrderResponseSchema]]
)
async def get_order(
    order_query: OrderReadSchema,
    order_service: OrderService = Depends(get_order_service),
):
    order = None
    if order_query.id:
        order = await order_service.read_by_id(id=order_query.id)
    elif order_query.portfolio_id:
        order = await order_service.read_orders_by_portfolio_id(
            portfolio_id=order_query.portfolio_id
        )
    else:
        raise HTTPException(
            status_code=400, detail="one of portfolio_id or order_id must be given!!"
        )
    if order:
        return order
    raise HTTPException(status_code=404, detail="order not found")


@order_router.post("", response_model=OrderResponseSchema)
async def create_order(
    order_create_schema: OrderCreateSchema,
    matching_engine: MatchingEngine = Depends(get_matching_engine),
):
    try:
        return await matching_engine.create_order(
            portfolio_id=order_create_schema.portfolio_id,
            market=order_create_schema.market,
            price=order_create_schema.price,
            size=order_create_schema.size,
            side=order_create_schema.side,
            order_type=order_create_schema.type,
        )
    except InvalidOrder as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
