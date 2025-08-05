from fifi import GetLogger
import pytest
from unittest.mock import patch
from httpx import ASGITransport, AsyncClient
from main import app
from fastapi.encoders import jsonable_encoder

from src.services import PositionService
from src.schemas.position_schema import PositionResponseSchema
from tests.materials import *

LOGGER = GetLogger().get()


@pytest.mark.asyncio
class TestPositionRouter:
    position_service = PositionService()

    async def create_position(self, position_factory):
        position_schemas = position_factory()
        return await self.position_service.create_many(data=position_schemas)

    async def test_position_read_by_id(self, database_provider_test, position_factory):
        positions = await self.create_position(position_factory)
        position = positions[-1]
        with patch.object(
            PositionService, "read_by_id", return_value=position
        ) as mock_method:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test/exapi/v1"
            ) as ac:
                response = await ac.get(f"/position?position_id={position.id}")
                assert response.status_code == 200
                LOGGER.info(f"position response: {response.json()}")
                assert response.json() == jsonable_encoder(
                    PositionResponseSchema(**position.to_dict())
                )
                mock_method.assert_awaited_once_with(id_=position.id)
