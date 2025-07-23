from fastapi import APIRouter, FastAPI
from contextlib import asynccontextmanager
from .portfolio_router import portfolio_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # initialize
    yield
    # cleanup


router = APIRouter(prefix="/v1", tags=["v1"], lifespan=lifespan)


router.include_router(portfolio_router)
