from fastapi import APIRouter, FastAPI
from contextlib import asynccontextmanager
from ..common.settings import Setting


setting = Setting()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # initialize
    yield
    # cleanup


base_router = APIRouter(
    prefix=f"/{setting.API_VERSION}", tags=["ExchangeAPIs"], lifespan=lifespan
)
