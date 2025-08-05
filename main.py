from fastapi import FastAPI
from fifi import GetLogger
from src import Setting, base_router


LOGGER = GetLogger().get()
setting = Setting()

# Create fastapi server
app = FastAPI(
    openapi_url=f"/{setting.API_PREFIX}/openapi.json",  # Customize the OpenAPI schema URL
    docs_url=f"/{setting.API_PREFIX}/docs",  # Customize the Swagger UI URL
)

app.include_router(base_router, prefix=f"/{setting.API_PREFIX}")
