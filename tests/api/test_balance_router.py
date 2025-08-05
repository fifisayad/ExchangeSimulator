from fifi import GetLogger
import pytest
import logging
from unittest.mock import patch
from httpx import ASGITransport, AsyncClient
from main import app
from fastapi.encoders import jsonable_encoder

from src.services import BalanceService
from src.schemas.balance_schema import BalanceDepositSchema, BalanceResponseSchema
from src.services.portfolio_service import PortfolioService
from tests.materials import *


LOGGER = logging.getLogger(__name__)


@pytest.mark.asyncio
class TestBalanceRouter:
    balance_service = BalanceService()
    portfolio_service = PortfolioService()

    async def create_balance(self, balance_factory_for_portfolios):
        balance_schemas = balance_factory_for_portfolios("iamrich")
        return await self.balance_service.create_many(data=balance_schemas)

    async def test_balance_read_by_id(
        self, database_provider_test, balance_factory_for_portfolios
    ):
        balances = await self.create_balance(balance_factory_for_portfolios)
        balance = balances[-1]
        with patch.object(
            BalanceService, "read_by_id", return_value=balance
        ) as mock_method:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test/exapi/v1"
            ) as ac:
                response = await ac.get(f"/balance?asset_id={balance.id}")
                assert response.status_code == 200
                LOGGER.info(f"balance response: {response.json()}")
                assert response.json() == jsonable_encoder(
                    BalanceResponseSchema(**balance.to_dict())
                )
                mock_method.assert_awaited_once_with(id_=balance.id)

    async def test_balance_read_by_id_failed(
        self, database_provider_test, balance_factory_for_portfolios
    ):
        with patch.object(
            BalanceService, "read_by_id", return_value=None
        ) as mock_method:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test/exapi/v1"
            ) as ac:
                response = await ac.get(f"/balance?asset_id=SHIT")
                assert response.status_code == 404
                LOGGER.info(f"balance response: {response.json()}")

                mock_method.assert_awaited_once_with(id_="SHIT")

    async def test_balance_read_by_portfolio_id(
        self, database_provider_test, balance_factory_for_portfolios
    ):
        balances = await self.create_balance(balance_factory_for_portfolios)
        balance = balances[-1]
        with patch.object(
            BalanceService, "read_many_by_portfolio_id", return_value=balances
        ) as mock_method:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test/exapi/v1"
            ) as ac:
                response = await ac.get(f"/balance?portfolio_id={balance.portfolio_id}")
                assert response.status_code == 200
                LOGGER.info(f"balance response: {response.json()}")
                expected_list = []
                for _balance in balances:
                    expected_list.append(
                        jsonable_encoder(BalanceResponseSchema(**_balance.to_dict()))
                    )
                assert response.json() == expected_list
                mock_method.assert_awaited_once_with(
                    portfolio_id=balance.portfolio_id,
                )

    async def test_balance_read_by_portfolio_id_failed(self, database_provider_test):
        with patch.object(
            BalanceService, "read_many_by_portfolio_id", return_value=[]
        ) as mock_method:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test/exapi/v1"
            ) as ac:
                response = await ac.get(f"""/balance?portfolio_id=sdf""")
                assert response.status_code == 404
                LOGGER.info(f"balance response: {response.json()}")
                mock_method.assert_awaited_once_with(
                    portfolio_id="sdf",
                )

    async def test_balance_read_by_asset(
        self, database_provider_test, balance_factory_for_portfolios
    ):
        balances = await self.create_balance(balance_factory_for_portfolios)
        balance = balances[-1]
        with patch.object(
            BalanceService, "read_by_asset", return_value=balance
        ) as mock_method:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test/exapi/v1"
            ) as ac:
                response = await ac.get(
                    f"/balance?portfolio_id={balance.portfolio_id}&asset={balance.asset.value}"
                )
                assert response.status_code == 200
                LOGGER.info(f"balance response: {response.json()}")
                assert response.json() == jsonable_encoder(
                    BalanceResponseSchema(**balance.to_dict())
                )
                mock_method.assert_awaited_once_with(
                    portfolio_id=balance.portfolio_id, asset=balance.asset
                )

    async def test_balance_read_by_asset_failed(self, database_provider_test):
        with patch.object(
            BalanceService, "read_many_by_portfolio_id", return_value=None
        ) as mock_method_portfolio:
            with patch.object(
                BalanceService, "read_by_asset", return_value=None
            ) as mock_method_asset:
                async with AsyncClient(
                    transport=ASGITransport(app=app), base_url="http://test/exapi/v1"
                ) as ac:
                    response = await ac.get(
                        f"""/balance?portfolio_id=h1&asset={Asset.BTC.value}"""
                    )
                    assert response.status_code == 404
                    LOGGER.info(f"balance response: {response.json()}")

                    mock_method_asset.assert_awaited_once_with(
                        portfolio_id="h1", asset=Asset.BTC
                    )

    async def test_deposit_balance_update(
        self, database_provider_test, balance_factory_for_portfolios
    ):
        balances = await self.create_balance(balance_factory_for_portfolios)
        balance = balances[-1]
        with patch.object(
            BalanceService, "add_balance", return_value=True
        ) as mock_method_add:
            with patch.object(
                BalanceService, "read_by_asset", return_value=balance
            ) as mock_method_read:
                async with AsyncClient(
                    transport=ASGITransport(app=app), base_url="http://test/exapi/v1"
                ) as ac:
                    response = await ac.patch(
                        f"/balance/deposit",
                        json=jsonable_encoder(
                            BalanceDepositSchema(
                                portfolio_id=balance.portfolio_id,
                                asset=Asset.BTC,
                                quantity=0.1,
                            )
                        ),
                    )
                    assert response.status_code == 200
                    LOGGER.info(f"balance response: {response.json()}")
                    assert response.json() == jsonable_encoder(
                        BalanceResponseSchema(**balance.to_dict())
                    )
                    mock_method_add.assert_awaited_once_with(
                        portfolio_id=balance.portfolio_id,
                        asset=Asset.BTC,
                        qty=0.1,
                    )
                    mock_method_read.assert_awaited_once_with(
                        portfolio_id=balance.portfolio_id, asset=Asset.BTC
                    )

    async def test_deposit_balance_create(
        self, database_provider_test, balance_factory_for_portfolios
    ):
        balances = await self.create_balance(balance_factory_for_portfolios)
        portfolio = await self.portfolio_service.create(
            data=PortfolioSchema(name="iamrich")
        )
        balance = balances[-1]
        with patch.object(
            BalanceService, "add_balance", return_value=False
        ) as mock_method_add:
            with patch.object(
                PortfolioService, "read_by_id", return_value=portfolio
            ) as mock_method_portfolio_read:
                with patch.object(
                    BalanceService, "create_by_qty", return_value=balance
                ) as mock_method_create:
                    async with AsyncClient(
                        transport=ASGITransport(app=app),
                        base_url="http://test/exapi/v1",
                    ) as ac:
                        response = await ac.patch(
                            f"/balance/deposit",
                            json=jsonable_encoder(
                                BalanceDepositSchema(
                                    portfolio_id=balance.portfolio_id,
                                    asset=Asset.BTC,
                                    quantity=0.1,
                                )
                            ),
                        )
                        assert response.status_code == 200
                        LOGGER.info(f"balance response: {response.json()}")
                        assert response.json() == jsonable_encoder(
                            BalanceResponseSchema(**balance.to_dict())
                        )
                        mock_method_add.assert_awaited_once_with(
                            portfolio_id=balance.portfolio_id,
                            asset=Asset.BTC,
                            qty=0.1,
                        )
                        mock_method_portfolio_read.assert_awaited_once_with(
                            id_=balance.portfolio_id
                        )
                        mock_method_create.assert_awaited_once_with(
                            portfolio_id=balance.portfolio_id,
                            asset=Asset.BTC,
                            qty=0.1,
                        )

    async def test_create_balance_failed(
        self, database_provider_test, balance_factory_for_portfolios
    ):
        balances = await self.create_balance(balance_factory_for_portfolios)
        portfolio = await self.portfolio_service.create(
            data=PortfolioSchema(name="iamrich")
        )
        balance = balances[-1]
        with patch.object(
            BalanceService, "add_balance", return_value=False
        ) as mock_method_add:
            with patch.object(
                PortfolioService, "read_by_id", return_value=None
            ) as mock_method_portfolio_read:
                with patch.object(
                    BalanceService, "create_by_qty", return_value=balance
                ) as mock_method_create:
                    async with AsyncClient(
                        transport=ASGITransport(app=app),
                        base_url="http://test/exapi/v1",
                    ) as ac:
                        response = await ac.patch(
                            f"/balance/deposit",
                            json=jsonable_encoder(
                                BalanceDepositSchema(
                                    portfolio_id=balance.portfolio_id,
                                    asset=Asset.BTC,
                                    quantity=0.1,
                                )
                            ),
                        )
                        assert response.status_code == 400
                        LOGGER.info(f"balance response: {response.json()}")
                        mock_method_add.assert_awaited_once_with(
                            portfolio_id=balance.portfolio_id,
                            asset=Asset.BTC,
                            qty=0.1,
                        )
                        mock_method_portfolio_read.assert_awaited_once_with(
                            id_=balance.portfolio_id
                        )
                        mock_method_create.assert_not_awaited()
