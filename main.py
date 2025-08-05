import coloredlogs
import logging
from fastapi import FastAPI
from src import Setting, base_router


coloredlogs.install()
LOGGER = logging.getLogger(__name__)
name_to_level = logging.getLevelNamesMapping()
logging.basicConfig(
    level=name_to_level["INFO"],
    format="[%(asctime)s] [%(levelname)s] [%(funcName)s] %(message)s",
)

setting = Setting()

# Create fastapi server
app = FastAPI(
    openapi_url=f"/{setting.API_PREFIX}/openapi.json",  # Customize the OpenAPI schema URL
    docs_url=f"/{setting.API_PREFIX}/docs",  # Customize the Swagger UI URL
)

app.include_router(base_router, prefix=f"/{setting.API_PREFIX}")
