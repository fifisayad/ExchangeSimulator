from typing import List, Union
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from contextlib import asynccontextmanager

from ...schemas.order_schema import OrderReadSchema, OrderResponseSchema
from .deps import get_order_service
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
